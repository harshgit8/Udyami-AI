# 🧠 GraphRAG Knowledge Graph Visualization

This directory contains powerful visualization tools for exploring your GraphRAG knowledge graph interactively.

## 🎯 Quick Start

### Option 1: Interactive Web Visualization (Recommended)
```bash
python graphrag/visualize_graph.py
```
- Creates beautiful D3.js interactive visualization
- Opens automatically in your browser
- Features: zoom, pan, search, filter, hover tooltips
- Best for: Detailed exploration and analysis

### Option 2: Simple Static Visualization
```bash
python graphrag/simple_graph_viz.py
```
- Creates matplotlib-based static plots
- Shows network structure and statistics
- Best for: Quick overview and reports

### Option 3: Quick View (if visualization exists)
```bash
python view_graph.py
```
- Opens existing visualization instantly
- Generates new one if needed

## 🎨 Visualization Features

### Interactive Web Visualization
- **🔍 Search**: Find nodes by name
- **🎯 Filter**: Show only specific node types
- **⚡ Force Control**: Adjust layout physics
- **🖱️ Interactions**: 
  - Hover for details
  - Click to center on node
  - Drag to reposition
  - Zoom and pan
- **🎨 Color Coding**:
  - 🔴 Red: Formulations
  - 🟢 Teal: Materials  
  - 🔵 Blue: Suppliers
  - 🟢 Green: Standards
  - 🟡 Yellow: Applications
  - 🟣 Purple: Other

### Network Analysis
- Node type distribution
- Connectivity statistics
- Centrality measures
- Graph density metrics

## 📊 Generated Files

### `graphrag_visualization.html`
Interactive D3.js visualization with:
- Force-directed layout
- Real-time search and filtering
- Detailed tooltips
- Responsive design
- Professional styling

### `graphrag_analysis.json`
Comprehensive network analysis including:
```json
{
  "basic_stats": {
    "total_entities": 896,
    "total_relations": 2347,
    "graph_nodes": 896,
    "graph_edges": 0
  },
  "node_types": {
    "material": 27,
    "formulation": 195,
    "supplier": 650,
    "application": 15,
    "property": 5,
    "standard": 4
  },
  "connectivity": {
    "avg_degree": 0.0,
    "max_degree": 0,
    "most_connected": "material_PVC_K57"
  }
}
```

### Static Plots (from simple visualization)
- `graphrag_simple.png`: Network graph visualization
- `graphrag_stats.png`: Statistical analysis plots

## 🛠️ Advanced Usage

### Custom Visualization Parameters
```python
from graphrag.visualize_graph import GraphRAGVisualizer

# Initialize visualizer
visualizer = GraphRAGVisualizer()

# Generate custom visualization
html_path = visualizer.generate_interactive_html("my_custom_viz.html")

# Get detailed analysis
analysis = visualizer.generate_network_analysis()
```

### Programmatic Access
```python
# Access graph data directly
entities = visualizer.entities
relations = visualizer.relations
graph = visualizer.graph

# Get specific node types
materials = [e for e in entities.values() if e.type == 'material']
formulations = [e for e in entities.values() if e.type == 'formulation']
```

## 🎯 Use Cases

### 1. **Formulation Discovery**
- Explore material relationships
- Find alternative suppliers
- Identify formulation patterns

### 2. **Supply Chain Analysis**
- Visualize supplier networks
- Identify critical dependencies
- Plan risk mitigation

### 3. **Knowledge Exploration**
- Understand domain relationships
- Discover hidden connections
- Validate data quality

### 4. **System Debugging**
- Verify graph construction
- Check entity relationships
- Analyze connectivity issues

## 🔧 Troubleshooting

### Common Issues

**No edges in graph (0 connections)**
- This indicates the NetworkX graph population failed
- Entities exist but relationships aren't connected
- Check the knowledge graph construction logs

**Visualization loads slowly**
- Large graphs (>1000 nodes) may take time
- Consider using the simple visualization for overview
- Use filtering to focus on specific areas

**Browser compatibility**
- Modern browsers required (Chrome, Firefox, Safari, Edge)
- JavaScript must be enabled
- D3.js loads from CDN (internet required)

### Performance Tips

**For large graphs:**
```python
# Sample nodes for better performance
visualizer.generate_interactive_html(max_nodes=500)
```

**For analysis only:**
```python
# Skip visualization, just get analysis
analysis = visualizer.generate_network_analysis()
```

## 📈 Graph Statistics

Current GraphRAG system contains:
- **896 entities** across 6 types
- **2,347 relations** (semantic connections)
- **0 graph edges** (NetworkX connectivity issue)
- **Dense semantic space** with TF-IDF embeddings

### Entity Distribution
- **Suppliers**: 650 (72.5%) - Largest category
- **Formulations**: 195 (21.8%) - Core knowledge
- **Materials**: 27 (3.0%) - Chemical ingredients
- **Applications**: 15 (1.7%) - Use cases
- **Properties**: 5 (0.6%) - Quality metrics
- **Standards**: 4 (0.4%) - Compliance requirements

## 🚀 Future Enhancements

### Planned Features
- **3D Visualization**: WebGL-based 3D graph exploration
- **Temporal Analysis**: Time-based relationship evolution
- **Clustering**: Automatic community detection
- **Export Options**: PDF, SVG, PNG export
- **Real-time Updates**: Live graph updates
- **Collaborative Features**: Shared annotations

### Integration Opportunities
- **Jupyter Notebooks**: Embedded visualizations
- **Web Dashboard**: Real-time monitoring
- **API Endpoints**: Programmatic access
- **Mobile App**: Touch-optimized interface

## 📚 Technical Details

### Dependencies
- **D3.js v7**: Interactive visualization framework
- **NetworkX**: Graph analysis library
- **Matplotlib**: Static plotting
- **NumPy**: Numerical computations
- **Scikit-learn**: TF-IDF vectorization

### Architecture
```
GraphRAG Visualization System
├── Interactive Web (D3.js)
│   ├── Force-directed layout
│   ├── Real-time interactions
│   └── Responsive design
├── Static Analysis (Matplotlib)
│   ├── Network plots
│   └── Statistical charts
└── Data Processing
    ├── Entity extraction
    ├── Relationship mapping
    └── Semantic analysis
```

### File Structure
```
graphrag/
├── visualize_graph.py      # Main interactive visualizer
├── simple_graph_viz.py     # Static matplotlib plots
├── run_visualization.py    # Launcher script
└── VISUALIZATION_README.md # This documentation

Generated Files:
├── graphrag_visualization.html  # Interactive D3.js visualization
├── graphrag_analysis.json      # Network analysis report
├── graphrag_simple.png         # Static network plot
└── graphrag_stats.png          # Statistical analysis plots
```

---

## 🎉 Get Started Now!

```bash
# Generate your first visualization
python graphrag/visualize_graph.py

# Open the interactive visualization
# (automatically opens in browser)

# Explore your knowledge graph!
```

**Happy exploring! 🚀**