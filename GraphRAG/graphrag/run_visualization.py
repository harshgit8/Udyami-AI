#!/usr/bin/env python3
"""Quick launcher for GraphRAG visualizations."""

import sys
import argparse
from pathlib import Path

def main():
    """Main launcher function."""
    
    parser = argparse.ArgumentParser(description="GraphRAG Visualization Launcher")
    parser.add_argument("--type", choices=["interactive", "simple", "both"], 
                       default="interactive", help="Type of visualization")
    parser.add_argument("--max-nodes", type=int, default=100, 
                       help="Maximum nodes for simple visualization")
    
    args = parser.parse_args()
    
    print("🚀 GraphRAG Visualization Launcher")
    print("="*50)
    
    if args.type in ["interactive", "both"]:
        print("\\n🌐 Launching Interactive Visualization...")
        try:
            from visualize_graph import main as interactive_main
            interactive_main()
        except Exception as e:
            print(f"❌ Interactive visualization failed: {e}")
    
    if args.type in ["simple", "both"]:
        print("\\n📊 Launching Simple Visualization...")
        try:
            from simple_graph_viz import main as simple_main
            simple_main()
        except Exception as e:
            print(f"❌ Simple visualization failed: {e}")
    
    print("\\n✅ Visualization launcher completed!")

if __name__ == "__main__":
    main()