import math
import random


class RoadGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.adj = {}

    def add_node(self, x, y, node_id=None):
        if node_id is None:
            node_id = len(self.nodes)
        self.nodes.append((x, y))
        if node_id not in self.adj:
            self.adj[node_id] = set()
        return node_id

    def add_edge(self, a, b):
        self.edges.append((a, b))
        self.adj[a].add(b)
        self.adj[b].add(a)

    def node_count(self):
        return len(self.nodes)


def generate_procedural_road_graph(radius, main_spacing, sub_spacing, perturbation_pct, seed):
    rng = random.Random(seed)
    graph = RoadGraph()

    perturbation = main_spacing * (perturbation_pct / 100.0)

    main_nodes = []
    half = int(radius / main_spacing) + 1
    for i in range(-half, half + 1):
        for j in range(-half, half + 1):
            x = i * main_spacing + rng.uniform(-perturbation, perturbation)
            y = j * main_spacing + rng.uniform(-perturbation, perturbation)
            if x * x + y * y > (radius * 1.2) ** 2:
                continue
            nid = graph.add_node(x, y)
            main_nodes.append((i, j, nid))

    node_map = {}
    for i, j, nid in main_nodes:
        node_map[(i, j)] = nid

    for i, j, nid in main_nodes:
        if (i + 1, j) in node_map:
            graph.add_edge(nid, node_map[(i + 1, j)])
        if (i, j + 1) in node_map:
            graph.add_edge(nid, node_map[(i, j + 1)])

    for idx, (i, j, nid) in enumerate(main_nodes):
        if (i + 1, j) in node_map and (i, j + 1) in node_map:
            n_right = node_map[(i + 1, j)]
            n_up = node_map[(i, j + 1)]
            if (i + 1, j + 1) in node_map:
                n_diag = node_map[(i + 1, j + 1)]
                x1, y1 = graph.nodes[n_right]
                x2, y2 = graph.nodes[n_up]
                mx = (x1 + x2) / 2.0 + rng.uniform(-perturbation * 0.5, perturbation * 0.5)
                my = (y1 + y2) / 2.0 + rng.uniform(-perturbation * 0.5, perturbation * 0.5)
                sub_nid = graph.add_node(mx, my)
                graph.add_edge(sub_nid, n_right)
                graph.add_edge(sub_nid, n_up)
                graph.add_edge(sub_nid, n_diag)
                graph.add_edge(sub_nid, nid)

    for nid in list(graph.adj.keys()):
        if len(graph.adj[nid]) < 2:
            for neighbor in list(graph.adj[nid]):
                graph.adj[neighbor].discard(nid)
            graph.adj[nid].clear()

    valid_nodes = [nid for nid in graph.adj if len(graph.adj[nid]) >= 2]
    valid_edges = [(a, b) for a, b in graph.edges if a in graph.adj and b in graph.adj and len(graph.adj[a]) >= 2 and len(graph.adj[b]) >= 2]

    clean_graph = RoadGraph()
    node_remap = {}
    for nid in valid_nodes:
        new_id = clean_graph.add_node(graph.nodes[nid][0], graph.nodes[nid][1], node_id=len(clean_graph.nodes) - 1)
        node_remap[nid] = new_id

    for a, b in valid_edges:
        clean_graph.add_edge(node_remap[a], node_remap[b])

    return clean_graph
