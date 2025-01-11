import numpy as np
import networkx as nx
from collections import defaultdict
import itertools
import os

class Node:
    def __init__(self, nid: int):
        self.nid = nid
        self.coordinates = []

class Element:
    def __init__(self, eid: int):
        self.eid = eid
        self.attached_nodes = []

class Edge:
    def __init__(self, edge_id: int, eid: int):
        self.edge_id = edge_id
        self.eid = eid
        self.attached_nodes = []

def parse_input_deck(input_file):
    """Parse the input deck to extract nodes, elements, and edges."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

    with open(input_file, 'r') as file:
        lines = [line.strip() for line in file]

    nodes = {}
    elements = {}
    edges = {}

    edge_id = 1
    node_block = False
    element_block = False

    for line in lines:
        # Detect start of node block
        if line.lower().startswith("*node"):
            node_block = True
            element_block = False
            continue

        # Detect start of element block
        if line.lower().startswith("*element"):
            element_block = True
            node_block = False
            continue

        # Skip comments
        if line.startswith('**'):
            node_block = False
            element_block = False
            continue

        # Parse nodes
        if node_block:
            parts = line.split(',')
            node_id = int(parts[0])
            nodes[node_id] = Node(node_id)
            nodes[node_id].coordinates = [float(i) for i in parts[1:]]

        # Parse elements and edges
        if element_block:
            parts = line.split(',')
            element_id = int(parts[0])
            elements[element_id] = Element(element_id)
            elements[element_id].attached_nodes = [int(i) for i in parts[1:]]

            # Create edges for the element
            num_nodes = len(elements[element_id].attached_nodes)
            for i in range(num_nodes):
                node_start = elements[element_id].attached_nodes[i]
                node_end = elements[element_id].attached_nodes[(i + 1) % num_nodes]  # Loop back to start for last edge
                edges[edge_id] = Edge(edge_id, element_id)
                edges[edge_id].attached_nodes = [node_start, node_end]
                edge_id += 1

    return nodes, elements, edges



def find_node_pairs_with_single_edge(edges):
    """
    Use NetworkX to find node pairs that share exactly one edge.
    
    Args:
        edges (dict): A dictionary of edges where key is edge_id and value is Edge object.
    
    Returns:
        dict: A dictionary where the key is a node pair (tuple) and the value is the corresponding edge ID.
    """
    # Step 1: Create a graph
    G = nx.MultiGraph()  # MultiGraph allows multiple edges between the same nodes
    
    # Add edges to the graph
    for edge_id, edge in edges.items():
        node_pair = tuple(sorted(edge.attached_nodes))  # Ensure consistent ordering
        G.add_edge(node_pair[0], node_pair[1], edge_id=edge_id)
    
    # Step 2: Find node pairs with exactly one edge
    single_edge_node_pairs = {}
    
    for u, v, data in G.edges(data=True):
        # Check if there's only one edge between the nodes
        if G.number_of_edges(u, v) == 1:
            edge_id = data["edge_id"]  # Get the edge ID from edge data
            single_edge_node_pairs[(u, v)] = edge_id

    return single_edge_node_pairs



# def cala

def main(input_file):
    nodes, elements, edges = parse_input_deck(input_file)

    # Example debug outputs
    print(f"Parsed {len(nodes)} nodes.")
    print(f"Parsed {len(elements)} elements.")
    print(f"Generated {len(edges)} edges.")

    # Find node pairs that share exactly one edge
    single_edge_node_pairs = find_node_pairs_with_single_edge(edges)
    
    print(f"Node pairs sharing exactly one edge: ")
    for k,v in single_edge_node_pairs.items():
        print(k,v)

# Example usage
if __name__ == "__main__":
    input_file = "plate_w_hole.inp"  # Replace with your Abaqus input deck file
    main(input_file)
