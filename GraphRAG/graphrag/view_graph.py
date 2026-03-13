#!/usr/bin/env python3
"""Quick command to view GraphRAG visualization."""

import webbrowser
import sys
from pathlib import Path

def main():
    """Quick launcher for GraphRAG visualization."""
    
    print("🚀 GraphRAG Visualization Quick Launcher")
    print("="*50)
    
    # Check for perfect visualization first
    perfect_viz = Path("perfect_graphrag_visualization.html")
    regular_viz = Path("graphrag_visualization.html")
    
    if perfect_viz.exists():
        print(f"✅ Found perfect visualization: {perfect_viz}")
        print("🌐 Opening in browser...")
        webbrowser.open(f"file://{perfect_viz.absolute()}")
    elif regular_viz.exists():
        print(f"✅ Found regular visualization: {regular_viz}")
        print("🌐 Opening in browser...")
        webbrowser.open(f"file://{regular_viz.absolute()}")
    else:
        print("❌ No visualization found. Generating new one...")
        try:
            # Generate new visualization
            import subprocess
            result = subprocess.run([sys.executable, "graphrag/visualize_graph.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Visualization generated successfully!")
                if regular_viz.exists():
                    webbrowser.open(f"file://{regular_viz.absolute()}")
            else:
                print(f"❌ Failed to generate visualization: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("🎯 Visualization commands:")
    print("   - Interactive: python graphrag/visualize_graph.py")
    print("   - Simple: python graphrag/simple_graph_viz.py")
    print("   - Quick view: python view_graph.py")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()