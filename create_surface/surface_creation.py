import numpy as np
import networkx as nx
from collections import defaultdict
import itertools
import os

def parse_input_deck(input_file):
    """Parse the input deck to extract elements and their nodes, and nodes' coordinates."""
    elements = {}
    nodes = {}
    
    with open(input_file, 'r') as file:
        lines = [line.strip() for line in file]
    

    node_block = False
    element_block = False
    for line in lines:
        # Detect start of node block
        if line.startswith("*NODE"):
            node_block = True
            element_block = False
            continue
        # Detect start of element block
        if line.strip().startswith("*ELEMENT"):
            element_block = True
            node_block = False
            continue
        # Dected other 
        if line.startswith('**'):
            node_block = False
            element_block = False
            continue
        # Parse nodes
        if node_block:
            parts = line.strip().split(',')
            node_id = int(parts[0])
            coords = tuple(map(float, parts[1:]))
            nodes[node_id] = coords
        # Parse elements
        if element_block:
            parts = line.strip().split(',')
            element_id = int(parts[0])
            element_nodes = tuple(map(int, parts[1:]))
            elements[element_id] = element_nodes
    
    return nodes, elements, lines

def calculate_normal(nodes, element_nodes):
    """Calculate the normal vector of a 2D element."""
    # Assuming element_nodes are in counter-clockwise order for 2D mesh    
    # Calculate two vectors from the quad's vertices
    vec1 = np.array(nodes[element_nodes[1]]) - np.array(nodes[element_nodes[0]])
    vec2 = np.array(nodes[element_nodes[2]]) - np.array(nodes[element_nodes[1]])
    # Compute the cross product
    normal = np.cross(vec1, vec2)

    return normal / np.linalg.norm(normal)

def angle_between_normals(normal1, normal2):
    """Calculate the angle (in degrees) between two normals."""
    # Compute the dot product
    dot_product = np.dot(normal1, normal2)
    # Clamp the dot product to avoid numerical issues
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    return (np.arccos(dot_product)/np.pi)*180

def build_nodes_to_elements_map(elements):
    """Build a map from nodes to elements for quick adjacency lookup."""
    nodes_to_elements = defaultdict(set)
    for elem_id, elem_nodes in elements.items():
        for node in elem_nodes:
            nodes_to_elements[node].add(elem_id)
    return nodes_to_elements

def split_surfaces(nodes, elements, angle_threshold):
    """Split the surface into groups using itertools for adjacency checking."""
    graph = nx.Graph()
    # Build a map of nodes to elements
    nodes_to_elements = build_nodes_to_elements_map(elements)
    # Precompute normals for all elements
    normals = {elem_id: calculate_normal(nodes, elem_nodes) for elem_id, elem_nodes in elements.items()}
    
    # Use itertools to loop over unique element pairs
    for connected_elements in nodes_to_elements.values():
        if len(connected_elements) > 1:
            for elem_id, other_elem_id in itertools.combinations(connected_elements, 2):
                # Calculate angle only for shared-node neighbors
                angle = angle_between_normals(normals[elem_id], normals[other_elem_id])
                if angle <= angle_threshold:
                    graph.add_edge(elem_id, other_elem_id)
    
    print(graph)
    
    # Group elements by connected components
    surface_groups = list(nx.connected_components(graph))

    return surface_groups
    
def main(input_file, output_folder, angle_threshold=50):
    
    nodes, elements, lines = parse_input_deck(input_file)

    surface_groups = split_surfaces(nodes, elements, angle_threshold)
     
    # Write surface definitions
    
    output_file = output_folder+'/'+input_file
    
    # Check if the directory exists
    if not os.path.exists(output_folder):
        # If it doesn't exist, create the directory
        os.makedirs(output_folder)
        print(f"Directory '{output_folder}' created.")
    else:
        pass
    
    with open(output_file, 'w') as file:
        for line in lines:
            file.write(f'{line}\n')
        for i, group in enumerate(surface_groups, start=1):
            file.write(f"*Surface, type=ELEMENT, name=SURF_AUTO_{i}\n")
            for elem_id in sorted(group):
                file.write(f"{elem_id}, SPOS\n")  # S1: surface of the element
    print(f"Surface definitions written to {output_file}")


# Example usage
input_file = "test_abq_2.inp"  # Replace with your Abaqus input deck file
output_folder = './out'
angle_threshold = 50  # Angle in degrees
main(input_file, output_folder, angle_threshold)
