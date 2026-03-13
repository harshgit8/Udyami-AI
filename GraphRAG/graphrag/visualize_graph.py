#!/usr/bin/env python3
"""GraphRAG Knowledge Graph Visualization System."""

import json
import sys
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
import networkx as nx
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from knowledge_graph import GraphRAGEngine
from config import Config
from logging_config import get_logger

logger = get_logger(__name__)


class GraphRAGVisualizer:
    """Interactive GraphRAG knowledge graph visualizer."""
    
    def __init__(self):
        """Initialize the visualizer."""
        try:
            print("🔄 Initializing GraphRAG Engine...")
            self.graphrag_engine = GraphRAGEngine()
            print("✅ GraphRAG Engine loaded successfully")
            
            # Get graph data
            self.graph = self.graphrag_engine.graph
            self.entities = self.graphrag_engine.entities
            self.relations = self.graphrag_engine.relations
            
            print(f"📊 Graph Statistics:")
            print(f"   - Entities: {len(self.entities)}")
            print(f"   - Relations: {len(self.relations)}")
            print(f"   - Graph Nodes: {self.graph.number_of_nodes()}")
            print(f"   - Graph Edges: {self.graph.number_of_edges()}")
            
        except Exception as e:
            print(f"❌ Failed to initialize GraphRAG visualizer: {e}")
            raise
    
    def generate_interactive_html(self, output_file: str = "graphrag_visualization.html") -> str:
        """Generate interactive HTML visualization using D3.js."""
        
        print("🎨 Generating interactive visualization...")
        
        # Prepare graph data for D3.js
        nodes_data = self._prepare_nodes_data()
        links_data = self._prepare_links_data()
        
        # Generate HTML with embedded D3.js visualization
        html_content = self._generate_html_template(nodes_data, links_data)
        
        # Write to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        abs_path = output_path.absolute()
        print(f"✅ Visualization saved to: {abs_path}")
        
        return str(abs_path)
    
    def _prepare_nodes_data(self) -> List[Dict[str, Any]]:
        """Prepare nodes data for visualization."""
        nodes = []
        
        # Add entity nodes
        for entity_id, entity_data in self.entities.items():
            # Handle GraphEntity objects
            if hasattr(entity_data, 'type'):
                node_type = entity_data.type
                name = entity_data.name
                properties = entity_data.properties
            else:
                # Fallback for dict-like objects
                node_type = self._determine_node_type(entity_data)
                name = entity_data.get('name', entity_id)
                properties = entity_data.get('properties', {})
            
            nodes.append({
                'id': entity_id,
                'name': name,
                'type': node_type,
                'category': node_type,  # Use type as category
                'properties': properties,
                'size': self._calculate_node_size(entity_id),
                'color': self._get_node_color(node_type),
                'description': self._get_node_description(entity_data)
            })
        
        return nodes
    
    def _prepare_links_data(self) -> List[Dict[str, Any]]:
        """Prepare links data for visualization."""
        links = []
        
        # Get all valid entity IDs
        valid_entity_ids = set(self.entities.keys())
        
        for relation in self.relations:
            # Handle GraphRelation objects
            if hasattr(relation, 'source_id'):
                source = relation.source_id
                target = relation.target_id
                rel_type = relation.relation_type
                weight = relation.weight
                confidence = relation.confidence
            else:
                # Fallback for dict-like objects
                source = relation.get('source', '')
                target = relation.get('target', '')
                rel_type = relation.get('type', 'related')
                weight = relation.get('weight', 1.0)
                confidence = relation.get('confidence', 0.5)
            
            # Only add links where both source and target entities exist
            if source and target and source in valid_entity_ids and target in valid_entity_ids:
                links.append({
                    'source': source,
                    'target': target,
                    'type': rel_type,
                    'weight': weight,
                    'confidence': confidence,
                    'description': f"{rel_type}: {source} → {target}"
                })
        
        return links
    
    def _determine_node_type(self, entity_data: Any) -> str:
        """Determine node type based on entity data."""
        # Handle GraphEntity objects
        if hasattr(entity_data, 'type'):
            return entity_data.type
        
        # Fallback for dict-like objects
        category = entity_data.get('category', '').lower()
        name = entity_data.get('name', '').lower()
        
        if 'formulation' in category or 'formula' in name:
            return 'formulation'
        elif 'material' in category or any(mat in name for mat in ['pvc', 'dop', 'caco3', 'tio2']):
            return 'material'
        elif 'supplier' in category or 'company' in name:
            return 'supplier'
        elif 'standard' in category or any(std in name for std in ['is_', 'astm', 'rohs']):
            return 'standard'
        elif 'application' in category:
            return 'application'
        else:
            return 'other'
    
    def _calculate_node_size(self, entity_id: str) -> int:
        """Calculate node size based on connectivity."""
        try:
            if self.graph.has_node(entity_id):
                degree = self.graph.degree(entity_id)
                return max(5, min(30, degree * 2))  # Size between 5-30
            return 8
        except:
            return 8
    
    def _get_node_color(self, node_type: str) -> str:
        """Get color for node type."""
        colors = {
            'formulation': '#FF6B6B',    # Red
            'material': '#4ECDC4',       # Teal
            'supplier': '#45B7D1',       # Blue
            'standard': '#96CEB4',       # Green
            'application': '#FFEAA7',    # Yellow
            'other': '#DDA0DD'           # Plum
        }
        return colors.get(node_type, '#999999')
    
    def _get_node_description(self, entity_data: Any) -> str:
        """Get description for node."""
        desc_parts = []
        
        # Handle GraphEntity objects
        if hasattr(entity_data, 'name'):
            name = entity_data.name
            node_type = entity_data.type
            properties = entity_data.properties
        else:
            # Fallback for dict-like objects
            name = entity_data.get('name', 'Unknown')
            node_type = entity_data.get('category', 'Unknown')
            properties = entity_data.get('properties', {})
        
        desc_parts.append(f"Name: {name}")
        desc_parts.append(f"Type: {node_type}")
        
        if properties:
            for key, value in list(properties.items())[:3]:  # Show first 3 properties
                desc_parts.append(f"{key}: {value}")
        
        return "\\n".join(desc_parts)
    
    def _generate_html_template(self, nodes_data: List[Dict], links_data: List[Dict]) -> str:
        """Generate complete HTML template with D3.js visualization."""
        
        # Convert data to JSON strings
        nodes_json = json.dumps(nodes_data, indent=2)
        links_json = json.dumps(links_data, indent=2)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GraphRAG Knowledge Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .header {{
            background: rgba(0,0,0,0.2);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 10px;
        }}
        
        .stat {{
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 20px;
            backdrop-filter: blur(5px);
        }}
        
        .controls {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            z-index: 1000;
        }}
        
        .control-group {{
            margin-bottom: 10px;
        }}
        
        .control-group label {{
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        
        .control-group input, .control-group select {{
            width: 100%;
            padding: 5px;
            border: none;
            border-radius: 5px;
            background: rgba(255,255,255,0.9);
            color: black;
        }}
        
        .legend {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            z-index: 1000;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            pointer-events: none;
            font-size: 0.9em;
            max-width: 300px;
            z-index: 1001;
        }}
        
        #graph-container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        .node {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 2px;
        }}
        
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        
        .node:hover {{
            stroke-width: 3px;
        }}
        
        .node.highlighted {{
            stroke: #ff0;
            stroke-width: 4px;
        }}
        
        .link.highlighted {{
            stroke: #ff0;
            stroke-width: 3px;
            stroke-opacity: 1;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 GraphRAG Knowledge Graph</h1>
        <div class="stats">
            <div class="stat">
                <strong>{len(nodes_data)}</strong> Entities
            </div>
            <div class="stat">
                <strong>{len(links_data)}</strong> Relations
            </div>
            <div class="stat">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
    </div>
    
    <div class="controls">
        <div class="control-group">
            <label>🔍 Search Nodes:</label>
            <input type="text" id="search-input" placeholder="Type to search...">
        </div>
        <div class="control-group">
            <label>🎯 Filter by Type:</label>
            <select id="type-filter">
                <option value="">All Types</option>
                <option value="formulation">Formulations</option>
                <option value="material">Materials</option>
                <option value="supplier">Suppliers</option>
                <option value="standard">Standards</option>
                <option value="application">Applications</option>
            </select>
        </div>
        <div class="control-group">
            <label>⚡ Force Strength:</label>
            <input type="range" id="force-slider" min="10" max="500" value="100">
        </div>
    </div>
    
    <div class="legend">
        <h4>🎨 Node Types</h4>
        <div class="legend-item">
            <div class="legend-color" style="background: #FF6B6B;"></div>
            <span>Formulations</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #4ECDC4;"></div>
            <span>Materials</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #45B7D1;"></div>
            <span>Suppliers</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #96CEB4;"></div>
            <span>Standards</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #FFEAA7;"></div>
            <span>Applications</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #DDA0DD;"></div>
            <span>Other</span>
        </div>
    </div>
    
    <div id="graph-container"></div>
    <div class="tooltip" id="tooltip" style="display: none;"></div>

    <script>
        // Graph data
        const nodes = {nodes_json};
        const links = {links_json};
        
        // Set up SVG
        const container = d3.select("#graph-container");
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = container.append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Add zoom behavior
        const g = svg.append("g");
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Set up force simulation
        let simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 5));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", d => Math.sqrt(d.weight * 2));
        
        // Create nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .style("fill", d => d.color)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add labels
        const label = g.append("g")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .text(d => d.name.length > 15 ? d.name.substring(0, 15) + "..." : d.name)
            .style("font-size", "10px")
            .style("fill", "white")
            .style("text-anchor", "middle")
            .style("pointer-events", "none")
            .style("text-shadow", "1px 1px 2px rgba(0,0,0,0.8)");
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        // Node interactions
        node.on("mouseover", function(event, d) {{
            tooltip.style("display", "block")
                .html(d.description)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
            
            // Highlight connected nodes and links
            highlightConnected(d);
        }})
        .on("mouseout", function() {{
            tooltip.style("display", "none");
            clearHighlights();
        }})
        .on("click", function(event, d) {{
            console.log("Node clicked:", d);
            // Center on clicked node
            const transform = d3.zoomIdentity
                .translate(width / 2 - d.x, height / 2 - d.y)
                .scale(1.5);
            svg.transition().duration(750).call(zoom.transform, transform);
        }});
        
        // Simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y + 4);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Highlight functions
        function highlightConnected(selectedNode) {{
            const connectedNodes = new Set();
            const connectedLinks = new Set();
            
            links.forEach(link => {{
                if (link.source.id === selectedNode.id || link.target.id === selectedNode.id) {{
                    connectedLinks.add(link);
                    connectedNodes.add(link.source.id);
                    connectedNodes.add(link.target.id);
                }}
            }});
            
            node.classed("highlighted", d => connectedNodes.has(d.id));
            link.classed("highlighted", d => connectedLinks.has(d));
        }}
        
        function clearHighlights() {{
            node.classed("highlighted", false);
            link.classed("highlighted", false);
        }}
        
        // Search functionality
        d3.select("#search-input").on("input", function() {{
            const searchTerm = this.value.toLowerCase();
            
            node.style("opacity", d => {{
                if (!searchTerm) return 1;
                return d.name.toLowerCase().includes(searchTerm) ? 1 : 0.2;
            }});
            
            label.style("opacity", d => {{
                if (!searchTerm) return 1;
                return d.name.toLowerCase().includes(searchTerm) ? 1 : 0.2;
            }});
        }});
        
        // Type filter
        d3.select("#type-filter").on("change", function() {{
            const selectedType = this.value;
            
            node.style("opacity", d => {{
                if (!selectedType) return 1;
                return d.type === selectedType ? 1 : 0.2;
            }});
            
            label.style("opacity", d => {{
                if (!selectedType) return 1;
                return d.type === selectedType ? 1 : 0.2;
            }});
        }});
        
        // Force strength control
        d3.select("#force-slider").on("input", function() {{
            const strength = -this.value;
            simulation.force("charge").strength(strength);
            simulation.alpha(0.3).restart();
        }});
        
        // Window resize
        window.addEventListener("resize", () => {{
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            
            svg.attr("width", newWidth).attr("height", newHeight);
            simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }});
        
        console.log("GraphRAG Visualization loaded successfully!");
        console.log(`Nodes: ${{nodes.length}}, Links: ${{links.length}}`);
    </script>
</body>
</html>
        """
        
        return html_template
    
    def generate_network_analysis(self) -> Dict[str, Any]:
        """Generate network analysis statistics."""
        
        print("📈 Generating network analysis...")
        
        analysis = {
            'basic_stats': {
                'total_entities': len(self.entities),
                'total_relations': len(self.relations),
                'graph_nodes': self.graph.number_of_nodes(),
                'graph_edges': self.graph.number_of_edges()
            },
            'node_types': {},
            'connectivity': {},
            'centrality': {},
            'clusters': {}
        }
        
        # Analyze node types
        type_counts = {}
        for entity_data in self.entities.values():
            # Handle GraphEntity objects
            if hasattr(entity_data, 'type'):
                node_type = entity_data.type
            else:
                node_type = self._determine_node_type(entity_data)
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        analysis['node_types'] = type_counts
        
        # Connectivity analysis
        if self.graph.number_of_nodes() > 0:
            degrees = dict(self.graph.degree())
            analysis['connectivity'] = {
                'avg_degree': sum(degrees.values()) / len(degrees) if degrees else 0,
                'max_degree': max(degrees.values()) if degrees else 0,
                'min_degree': min(degrees.values()) if degrees else 0,
                'most_connected': max(degrees, key=degrees.get) if degrees else None
            }
            
            # Centrality measures (for smaller graphs)
            if self.graph.number_of_nodes() < 1000:
                try:
                    betweenness = nx.betweenness_centrality(self.graph)
                    closeness = nx.closeness_centrality(self.graph)
                    
                    analysis['centrality'] = {
                        'top_betweenness': sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5],
                        'top_closeness': sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5]
                    }
                except:
                    analysis['centrality'] = {'error': 'Could not compute centrality measures'}
        
        return analysis
    
    def save_analysis_report(self, analysis: Dict[str, Any], output_file: str = "graphrag_analysis.json") -> str:
        """Save analysis report to JSON file."""
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        abs_path = output_path.absolute()
        print(f"📊 Analysis report saved to: {abs_path}")
        
        return str(abs_path)


def main():
    """Main function to generate GraphRAG visualization."""
    
    print("="*60)
    print("🎨 GRAPHRAG KNOWLEDGE GRAPH VISUALIZER")
    print("="*60)
    
    try:
        # Initialize visualizer
        visualizer = GraphRAGVisualizer()
        
        # Generate interactive visualization
        html_path = visualizer.generate_interactive_html()
        
        # Generate network analysis
        analysis = visualizer.generate_network_analysis()
        analysis_path = visualizer.save_analysis_report(analysis)
        
        # Print summary
        print("\\n📊 Network Analysis Summary:")
        print(f"   - Total Entities: {analysis['basic_stats']['total_entities']}")
        print(f"   - Total Relations: {analysis['basic_stats']['total_relations']}")
        print(f"   - Graph Density: {analysis['basic_stats']['graph_edges'] / max(1, analysis['basic_stats']['graph_nodes']):.2f}")
        
        print("\\n🎯 Node Types:")
        for node_type, count in analysis['node_types'].items():
            print(f"   - {node_type.title()}: {count}")
        
        if 'connectivity' in analysis:
            conn = analysis['connectivity']
            print(f"\\n🔗 Connectivity:")
            print(f"   - Average Degree: {conn.get('avg_degree', 0):.2f}")
            print(f"   - Most Connected: {conn.get('most_connected', 'N/A')}")
        
        print("\\n" + "="*60)
        print("🎉 VISUALIZATION GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"📁 HTML Visualization: {html_path}")
        print(f"📊 Analysis Report: {analysis_path}")
        print("\\n🌐 Opening visualization in browser...")
        
        # Open in browser
        webbrowser.open(f"file://{html_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)