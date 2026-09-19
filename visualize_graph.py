import networkx as nx
import matplotlib.pyplot as plt

from graph_database import (
    get_all_nodes,
    get_all_edges
)


nodes = get_all_nodes()
edges = get_all_edges()


G = nx.DiGraph()


# -------------------------
# ADD NODES
# -------------------------

for node in nodes:

    G.add_node(
        node["id"],
        label=node["label"],
        type=node["type"]
    )


# -------------------------
# ADD EDGES
# -------------------------

for edge in edges:

    G.add_edge(
        edge["source"],
        edge["target"],
        relationship=edge["relationship"]
    )


# -------------------------
# LAYOUT
# -------------------------

pos = nx.spring_layout(
    G,
    seed=42,
    k=2.5
)


# -------------------------
# GROUP NODE TYPES
# -------------------------

person_nodes = []
task_nodes = []
event_nodes = []
project_nodes = []


for node_id in G.nodes:

    node_type = G.nodes[node_id]["type"]

    if node_type == "Person":
        person_nodes.append(node_id)

    elif node_type == "Task":
        task_nodes.append(node_id)

    elif node_type == "Event":
        event_nodes.append(node_id)

    elif node_type == "Project":
        project_nodes.append(node_id)


# -------------------------
# DRAW EACH TYPE
# -------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=person_nodes,
    node_shape="o",
    node_size=3500,
    label="Person"
)

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=task_nodes,
    node_shape="s",
    node_size=3500,
    label="Task"
)

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=event_nodes,
    node_shape="D",
    node_size=3500,
    label="Event"
)

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=project_nodes,
    node_shape="h",
    node_size=4000,
    label="Project"
)


# -------------------------
# DRAW ARROWS
# -------------------------

nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    arrowstyle="-|>",
    arrowsize=25,
    width=2,
    connectionstyle="arc3,rad=0.05"
)


# -------------------------
# NODE LABELS
# -------------------------

labels = {}

for node_id in G.nodes:

    labels[node_id] = (
        G.nodes[node_id]["label"]
    )


nx.draw_networkx_labels(
    G,
    pos,
    labels=labels,
    font_size=8
)


# -------------------------
# RELATIONSHIP LABELS
# -------------------------

edge_labels = {}

for source, target, data in G.edges(data=True):

    edge_labels[
        (source, target)
    ] = data["relationship"]


nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    font_size=7,
    rotate=False
)


# -------------------------
# FINAL DISPLAY
# -------------------------

plt.title(
    "Student Smart Organizer - Graph Database",
    fontsize=16
)

plt.legend()

plt.axis("off")

plt.tight_layout()

plt.show()