import networkx as nx
import json
import os
from pathlib import Path
from ..orchestrator.config import settings

class GraphStore:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for concept relationships
        self.storage_path = settings.GRAPH_STORAGE_PATH
        
        # Ensure directory exists
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing graph if available
        if os.path.exists(self.storage_path):
            self.load()

    def close(self):
        """Save graph before closing"""
        self.save()

    def save(self):
        """Save graph to JSON file"""
        data = {
            'nodes': [
                {
                    'name': node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': edge[0],
                    'target': edge[1],
                    **self.graph.edges[edge]
                }
                for edge in self.graph.edges()
            ]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Load graph from JSON file"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing graph
            self.graph.clear()
            
            # Add nodes
            for node_data in data.get('nodes', []):
                name = node_data.pop('name')
                self.graph.add_node(name, **node_data)
            
            # Add edges
            for edge_data in data.get('edges', []):
                source = edge_data.pop('source')
                target = edge_data.pop('target')
                self.graph.add_edge(source, target, **edge_data)
                
        except Exception as e:
            print(f"Error loading graph: {e}")

    def query(self, query_type, parameters=None):
        """
        Execute a query on the graph.
        For compatibility with the original interface, supports basic operations.
        """
        parameters = parameters or {}
        
        # Simple test query
        if query_type == "RETURN 1 as num":
            return [{"num": 1}]
        
        # Add more query types as needed
        return []

    def add_concept(self, concept_name, definition, embedding_id, source_info):
        """Add a concept node to the graph"""
        self.graph.add_node(
            concept_name,
            definition=definition,
            embedding_id=embedding_id,
            source_doc=source_info.get('doc_id'),
            source_page=source_info.get('page'),
            node_type='concept'
        )
        self.save()
        return [{"name": concept_name}]

    def add_relation(self, source, target, relation_type, confidence):
        """Add a relationship edge between concepts"""
        if source in self.graph.nodes() and target in self.graph.nodes():
            self.graph.add_edge(
                source,
                target,
                relation_type=relation_type,
                confidence=confidence
            )
            self.save()
            return [{"source": source, "target": target, "type": relation_type}]
        return []

    def get_concept(self, concept_name):
        """Get a concept node and its properties"""
        if concept_name in self.graph.nodes():
            return {
                'name': concept_name,
                **self.graph.nodes[concept_name]
            }
        return None

    def get_related_concepts(self, concept_name, max_depth=2):
        """Get concepts related to the given concept within max_depth hops"""
        if concept_name not in self.graph.nodes():
            return []
        
        # Get neighbors within max_depth
        related = []
        visited = set()
        queue = [(concept_name, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
                
            visited.add(current)
            if current != concept_name:
                related.append({
                    'name': current,
                    'depth': depth,
                    **self.graph.nodes[current]
                })
            
            if depth < max_depth:
                for neighbor in self.graph.neighbors(current):
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
        
        return related

    def get_graph_stats(self):
        """Get statistics about the graph"""
        return {
            'num_concepts': self.graph.number_of_nodes(),
            'num_relations': self.graph.number_of_edges(),
            'density': nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0
        }
