import numpy as np
import networkx as nx
from collections import defaultdict
import itertools
import os

class Node:
    def __init__(self, nid: int):
        self.nid = int(nid)
        self.coordinates = []

class Element:
    def __init__(self, eid: int):
        self.eid = int(eid)
        self.attached_nodes = []

class Edge:
    def __init__(self, edge_id: int, attached_eid: int):
        self.edge_id = int(edge_id)
        self.attached_eid = int(attached_eid)
        self.attached_nodes = []
        self.vector = []
        
    def __repr__(self):
        return f"Edge(edge_id={self.edge_id}, attached_eid={self.attached_eid}, attached_nodes={self.attached_nodes})"

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
            nodes[node_id].coordinates = np.array([float(i) for i in parts[1:]])

        # Parse elements and edges
        if element_block:
            parts = line.split(',')
            element_id = int(parts[0])
            elements[element_id] = Element(element_id)
            elements[element_id].attached_nodes = np.array([int(i) for i in parts[1:]])

            # Create edges for the element
            num_nodes = len(elements[element_id].attached_nodes)
            for i in range(num_nodes):
                node_start = elements[element_id].attached_nodes[i]
                node_end = elements[element_id].attached_nodes[(i + 1) % num_nodes]  # Loop back to start for last edge
                edges[edge_id] = Edge(edge_id, element_id)
                edges[edge_id].attached_nodes = np.array([node_start, node_end])
                
                pA = nodes[node_start].coordinates
                pB = nodes[node_end].coordinates
                
                edges[edge_id].vector = (pA-pB)/np.linalg.norm(pA-pB)
                
                edge_id += 1

    return nodes, elements, edges

def angle_between_vectors(vector1, vector2):
    """Calculate the angle (in degrees) between two vectors."""
    # Compute the dot product
    dot_product = np.dot(vector1, vector2)
    # Clamp the dot product to avoid numerical issues
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    return (np.arccos(dot_product)/np.pi)*180

def detect_holes(edges):    
    
    nodes_to_edge_map = defaultdict(set)
    for edge in edges.values():        
        nodes_to_edge_map[tuple(sorted(edge.attached_nodes))].add(edge.edge_id)
        # print(edge.edge_id, edge.attached_eid, edge.attached_nodes, edge.vector)

    single_edges = defaultdict(set)
    for i in nodes_to_edge_map.values():
        if len(i) < 2:
            single_edges["single_edge"].add(list(i)[0])
    
    # Initialize graph
    graph = nx.Graph()
    for edge_id1, edge_id2 in itertools.combinations(single_edges["single_edge"], 2):
        edge1 = edges[edge_id1]
        edge2 = edges[edge_id2]

        # Check if edges share a node
        if len(set(edge1.attached_nodes) & set(edge2.attached_nodes)) > 0:
            # Check if edges are approximately parallel
            angle = angle_between_vectors(edge1.vector, edge2.vector)
            if angle not in [0,90,180,-90,-180]:  # Adjust the threshold for "parallelism"
                graph.add_edge(edge_id1, edge_id2)
    
    # Find connected components
    hole_groups = list(nx.connected_components(graph))

    return hole_groups

def main(input_file):
    
    print(f"Parsing input deck '{input_file}' ...")
    nodes, elements, edges = parse_input_deck(input_file)
    
    print(f'')

    print(f"    Parsed {len(nodes)} nodes.")
    print(f"    Parsed {len(elements)} elements.")
    print(f"    Generated {len(edges)} edges.")

    print(f'')
    
    hole_groups = detect_holes(edges)
    
    print(f"    Found {len(hole_groups)} holes in component.")
    print(hole_groups)
    
    print(f'Done.')

#------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    input_file = "plate_w_hole2.inp"  
    main(input_file)
