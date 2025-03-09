import os
import random
import networkx as nx
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from collections import defaultdict
import pickle

data_dir = "files"  # Directory containing ranking lists
progress_file = os.path.join(data_dir, "ranking_progress.pkl")

# Load a list from a chosen file
def load_items():
    files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]
    if not files:
        messagebox.showerror("Error", "No .txt files found in the directory.")
        return None
    
    file_path = filedialog.askopenfilename(initialdir=data_dir, title="Select a file",
                                           filetypes=[("Text files", "*.txt")])
    if not file_path:
        return None
    
    with open(file_path, "r") as f:
        items = [line.strip() for line in f if line.strip()]
    
    return items

# Graph data structures
graph = nx.DiGraph()
pairwise_comparisons = defaultdict(int)
used_matchups = set()  # Track used matchups to avoid repetition
total_matchups = 0
certainty = 0
current_pair = None  # Ensure global definition

def save_progress():
    with open(progress_file, "wb") as f:
        pickle.dump((graph, pairwise_comparisons, total_matchups, certainty, used_matchups), f)

def load_progress():
    global graph, pairwise_comparisons, total_matchups, certainty, used_matchups
    if os.path.exists(progress_file):
        with open(progress_file, "rb") as f:
            graph, pairwise_comparisons, total_matchups, certainty, used_matchups = pickle.load(f)

# GUI Components
root = tk.Tk()
root.title("Item Ranking")
root.geometry("600x400")  # Increase window size

label = tk.Label(root, text="Loading...", font=("Arial", 14))
label.pack()

button1 = tk.Button(root, text="Option 1", font=("Arial", 12), command=lambda: choose(0))
button2 = tk.Button(root, text="Option 2", font=("Arial", 12), command=lambda: choose(1))
button1.pack()
button2.pack()

certainty_label = tk.Label(root, text="Certainty: 0%", font=("Arial", 12))
certainty_label.pack()

matchups_label = tk.Label(root, text="Matchups Left: ?", font=("Arial", 12))
matchups_label.pack()

# Select items
items = load_items()
if not items:
    root.quit()

for item in items:
    graph.add_node(item)

load_progress()

def select_matchup():
    # Ensure no repeated matchups
    all_matchups = {(i, j) for i in items for j in items if i != j}
    available_matchups = all_matchups - used_matchups

    if not available_matchups:
        messagebox.showinfo("No more matchups", "All matchups have been completed!")
        root.quit()

    # Randomly choose from available matchups
    matchup = random.choice(list(available_matchups))
    used_matchups.add(matchup)

    return matchup

current_pair = select_matchup()

def choose(winner_idx):
    global total_matchups, certainty, current_pair
    loser_idx = 1 - winner_idx
    
    winner, loser = current_pair[winner_idx], current_pair[loser_idx]
    
    # Update graph
    if graph.has_edge(loser, winner):
        graph.remove_edge(loser, winner)
    graph.add_edge(winner, loser)
    
    pairwise_comparisons[winner] += 1
    pairwise_comparisons[loser] += 1
    total_matchups += 1
    
    # Compute new rankings
    ranks = nx.pagerank(graph)
    
    # Certainty factor (basic approximation)
    certainty = min(1, total_matchups / (len(items) * 10))
    remaining_matches = int((0.95 - certainty) * len(items) * 10)
    
    # Save progress
    save_progress()
    
    # Update GUI
    current_pair = select_matchup()
    label.config(text=f"Choose: {current_pair[0]} vs {current_pair[1]}")
    button1.config(text=current_pair[0])
    button2.config(text=current_pair[1])
    certainty_label.config(text=f"Certainty: {certainty * 100:.1f}%")
    matchups_label.config(text=f"Matchups Left: {max(0, remaining_matches)}")
    
    plot_graph(ranks)

fig, ax = plt.subplots(figsize=(8, 6))
def plot_graph(ranks):
    ax.clear()
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=False, node_size=[5000 * ranks[n] for n in graph.nodes],
            node_color='lightblue', edge_color='gray', ax=ax)
    ax.set_title("Current Ranking Visualization")
    plt.draw()
    plt.pause(0.1)

# Start first match
if items:
    label.config(text=f"Choose: {current_pair[0]} vs {current_pair[1]}")
    button1.config(text=current_pair[0])
    button2.config(text=current_pair[1])

plt.ion()
root.mainloop()
