"""Render the Neo4j knowledge graph to assets/graph.png for the README.

Dev-only dependency: pip install networkx matplotlib
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from neo4j import GraphDatabase

from app.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER


def main() -> None:
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        rows = driver.execute_query(
            "MATCH (s:Entity)-[r:REL]->(o:Entity) RETURN s.name AS s, r.type AS t, o.name AS o"
        ).records

    graph = nx.DiGraph()
    for row in rows:
        graph.add_edge(row["s"], row["o"], label=row["t"])

    labels = {node: textwrap.fill(str(node), 15) for node in graph.nodes}
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(graph, k=2.5, seed=42)
    nx.draw(
        graph,
        pos,
        labels=labels,
        node_size=2500,
        node_color="#9ecae1",
        edge_color="#999999",
        font_size=7,
        arrows=True,
        arrowsize=12,
    )
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=nx.get_edge_attributes(graph, "label"), font_size=5
    )
    Path("assets").mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig("assets/graph.png", dpi=150)
    print(f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges -> assets/graph.png")


if __name__ == "__main__":
    main()
