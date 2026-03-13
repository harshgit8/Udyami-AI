#!/usr/bin/env python3
"""Simple GraphRAG visualization using matplotlib."""

import sys
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from knowledge_graph import GraphRAGEngine
from logging_config import get_logger

logger = get_logger(__name__)


def create_simple_visualization(max_nodes: int = 100, output_file: str = "graphrag_simple.png"):
    """Create a simple matplotlib visualization of the GraphRAG knowledge graph."""
    
    print("🎨 Creating simple GraphRAG visualization...")
    
    try:
        # Initialize GraphRAG engine
        print("🔄 Loading GraphRAG engine...")
        graphrag_engine = GraphRAGEngine()
        
        # Get graph data
        graph = graphrag_engine.graph
        entities = graphrag_engine.entities
        
        print(f"📊 Original graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        # Sample nodes if graph is too large
        if graph.number_of_nodes() > max_nodes:
            print(f"🎯 Sampling {max_nodes} nodes from large graph...")
            
            # Get most connected nodes
            degrees = dict(graph.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            sampled_nodes = [node for node, degree in top_nodes]
            
            # Create subgraph
            viz_graph = graph.subgraph(sampled_nodes).copy()
        else:
            viz_graph = graph.copy()
        
        print(f"📈 Visualization graph: {viz_graph.number_of_nodes()} nodes, {viz_graph.number_of_edges()} edges")
        
        # Set up the plot
        plt.figure(figsize=(16, 12))
        plt.style.use('dark_background')
        
        # Create layout
        print("🎯 Computing graph layout...")
        if viz_graph.number_of_nodes() < 50:
            pos = nx.spring_layout(viz_graph, k=3, iterations=50)
        else:
            pos = nx.spring_layout(viz_graph, k=1, iterations=20)
        
        # Determine node colors and sizes based on type
        node_colors = []
        node_sizes = []
        
        color_map = {
            'formulation': '#FF6B6B',    # Red
            'material': '#4ECDC4',       # Teal  
            'supplier': '#45B7D1',       # Blue
            'standard': '#96CEB4',       # Green
            'application': '#FFEAA7',    # Yellow
            'other': '#DDA0DD'           # Plum
        }
        
        for node in viz_graph.nodes():
            entity_data = entities.get(node, {})
            
            # Determine node type - handle GraphEntity objects
            if hasattr(entity_data, 'type'):
                node_type = entity_data.type
                name = entity_data.name.lower()
            else:
                # Fallback for dict-like objects
                category = entity_data.get('category', '').lower()
                name = entity_data.get('name', '').lower()
                
                if 'formulation' in category or 'formula' in name:
                    node_type = 'formulation'
                elif 'material' in category or any(mat in name for mat in ['pvc', 'dop', 'caco3', 'tio2']):
                    node_type = 'material'
                elif 'supplier' in category or 'company' in name:
                    node_type = 'supplier'
                elif 'standard' in category or any(std in name for std in ['is_', 'astm', 'rohs']):
                    node_type = 'standard'
                elif 'application' in category:
                    node_type = 'application'
                else:
                    node_type = 'other'
            
            node_colors.append(color_map.get(node_type, '#999999'))
            
            # Size based on degree
            degree = viz_graph.degree(node)
            node_sizes.append(max(50, min(500, degree * 20)))
        
        # Draw the graph
        print("🎨 Drawing graph...")
        
        # Draw edges
        nx.draw_networkx_edges(viz_graph, pos, 
                              edge_color='#666666', 
                              alpha=0.5, 
                              width=0.5)
        
        # Draw nodes
        nx.draw_networkx_nodes(viz_graph, pos,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8)
        
        # Draw labels for important nodes (high degree)
        degrees = dict(viz_graph.degree())
        important_nodes = {}
        for node in viz_graph.nodes():
            if degrees.get(node, 0) > np.percentile(list(degrees.values()), 80):
                entity_data = entities.get(node, {})
                if hasattr(entity_data, 'name'):
                    name = entity_data.name[:10]
                else:
                    name = entity_data.get('name', node)[:10]
                important_nodes[node] = name
        
        nx.draw_networkx_labels(viz_graph, pos, 
                               labels=important_nodes,
                               font_size=8, 
                               font_color='white',
                               font_weight='bold')
        
        # Customize plot
        plt.title("GraphRAG Knowledge Graph Visualization", 
                 fontsize=20, fontweight='bold', color='white', pad=20)
        
        # Add legend
        legend_elements = []
        for node_type, color in color_map.items():
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                            markerfacecolor=color, markersize=10, 
                                            label=node_type.title()))
        
        plt.legend(handles=legend_elements, loc='upper right', 
                  frameon=True, fancybox=True, shadow=True)
        
        # Add statistics text
        stats_text = f"""Graph Statistics:
Nodes: {viz_graph.number_of_nodes()}
Edges: {viz_graph.number_of_edges()}
Density: {nx.density(viz_graph):.3f}
Avg Degree: {np.mean(list(degrees.values())):.1f}"""
        
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.8),
                color='white')
        
        plt.axis('off')
        plt.tight_layout()
        
        # Save the plot
        output_path = Path(output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        
        abs_path = output_path.absolute()
        print(f"✅ Simple visualization saved to: {abs_path}")
        
        # Show the plot
        plt.show()
        
        return str(abs_path)
        
    except Exception as e:
        print(f"❌ Simple visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_network_stats_plot(output_file: str = "graphrag_stats.png"):
    """Create statistical plots about the network."""
    
    print("📊 Creating network statistics plots...")
    
    try:
        # Initialize GraphRAG engine
        graphrag_engine = GraphRAGEngine()
        graph = graphrag_engine.graph
        entities = graphrag_engine.entities
        
        # Calculate statistics
        degrees = list(dict(graph.degree()).values())
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.patch.set_facecolor('black')
        
        # Degree distribution
        ax1.hist(degrees, bins=20, color='#4ECDC4', alpha=0.7, edgecolor='white')
        ax1.set_title('Degree Distribution', color='white', fontweight='bold')
        ax1.set_xlabel('Degree', color='white')
        ax1.set_ylabel('Frequency', color='white')
        ax1.tick_params(colors='white')
        ax1.set_facecolor('black')
        
        # Node type distribution
        type_counts = {}
        for entity_data in entities.values():
            if hasattr(entity_data, 'type'):
                node_type = entity_data.type
            else:
                node_type = entity_data.get('category', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        if type_counts:
            ax2.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
                   colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
            ax2.set_title('Node Type Distribution', color='white', fontweight='bold')
        
        # Connectivity over time (if we had temporal data, we'll simulate)
        ax3.plot(range(10), np.random.cumsum(np.random.randn(10)) + 100, 
                color='#FF6B6B', linewidth=2, marker='o')
        ax3.set_title('Network Growth (Simulated)', color='white', fontweight='bold')
        ax3.set_xlabel('Time Period', color='white')
        ax3.set_ylabel('Number of Connections', color='white')
        ax3.tick_params(colors='white')
        ax3.set_facecolor('black')
        
        # Top connected nodes
        top_nodes = sorted(dict(graph.degree()).items(), key=lambda x: x[1], reverse=True)[:10]
        node_names = []
        for node, degree in top_nodes:
            entity_data = entities.get(node, {})
            if hasattr(entity_data, 'name'):
                name = entity_data.name[:15]
            else:
                name = entity_data.get('name', node)[:15]
            node_names.append(name)
        node_degrees = [degree for node, degree in top_nodes]
        
        ax4.barh(range(len(node_names)), node_degrees, color='#96CEB4', alpha=0.8)
        ax4.set_yticks(range(len(node_names)))
        ax4.set_yticklabels(node_names, color='white')
        ax4.set_title('Top Connected Nodes', color='white', fontweight='bold')
        ax4.set_xlabel('Degree', color='white')
        ax4.tick_params(colors='white')
        ax4.set_facecolor('black')
        
        # Style all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        plt.suptitle('GraphRAG Network Analysis', fontsize=16, color='white', fontweight='bold')
        plt.tight_layout()
        
        # Save the plot
        output_path = Path(output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        
        abs_path = output_path.absolute()
        print(f"✅ Statistics plots saved to: {abs_path}")
        
        plt.show()
        
        return str(abs_path)
        
    except Exception as e:
        print(f"❌ Statistics plots failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function for simple visualization."""
    
    print("="*60)
    print("📊 SIMPLE GRAPHRAG VISUALIZATION")
    print("="*60)
    
    try:
        # Create simple network visualization
        viz_path = create_simple_visualization()
        
        # Create statistics plots
        stats_path = create_network_stats_plot()
        
        print("\\n" + "="*60)
        print("🎉 SIMPLE VISUALIZATIONS COMPLETED!")
        print("="*60)
        if viz_path:
            print(f"📁 Network Graph: {viz_path}")
        if stats_path:
            print(f"📊 Statistics: {stats_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple visualization failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)