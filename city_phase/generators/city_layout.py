import math
import random


class RoadGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.adj = {}
        self.edge_widths = {}  # (min(a,b), max(a,b)) -> width

    def add_node(self, x, y):
        node_id = len(self.nodes)
        self.nodes.append((x, y))
        self.adj[node_id] = set()
        return node_id

    def add_edge(self, a, b, width=8.0):
        key = (min(a, b), max(a, b))
        if key not in self.edges:
            self.edges.append(key)
            self.adj[a].add(b)
            self.adj[b].add(a)
            self.edge_widths[key] = width

    def node_count(self):
        return len(self.nodes)

    def get_edges_with_width(self):
        return [(a, b, self.edge_widths.get((min(a, b), max(a, b)), 8.0)) for a, b in self.edges]


def generate_road_graph(radius, main_spacing, sub_spacing, perturbation_pct, seed, road_mode="grid"):
    dispatch = {
        "grid": _generate_grid_road,
        "radial_ring": _generate_radial_ring_road,
        "organic": _generate_organic_road,
        "mixed": _generate_mixed_road,
    }
    if road_mode not in dispatch:
        road_mode = "grid"
    return dispatch[road_mode](radius, main_spacing, sub_spacing, perturbation_pct, seed)


def _cleanup_graph(graph):
    for nid in list(graph.adj.keys()):
        if len(graph.adj[nid]) < 2:
            for neighbor in list(graph.adj[nid]):
                graph.adj[neighbor].discard(nid)
            graph.adj[nid].clear()

    valid_nodes = [nid for nid in graph.adj if len(graph.adj[nid]) >= 2]
    valid_edges = [(a, b) for a, b in graph.edges if a in graph.adj and b in graph.adj and len(graph.adj[a]) >= 2 and len(graph.adj[b]) >= 2]

    clean = RoadGraph()
    remap = {}
    for nid in valid_nodes:
        remap[nid] = clean.add_node(graph.nodes[nid][0], graph.nodes[nid][1])
    for a, b in valid_edges:
        w = graph.edge_widths.get((min(a, b), max(a, b)), 8.0)
        clean.add_edge(remap[a], remap[b], width=w)
    return clean


# ============================================================
# Mode 1: Grid (enhanced with hierarchical subdivision)
# ============================================================
def _generate_grid_road(radius, main_spacing, sub_spacing, perturbation_pct, seed):
    rng = random.Random(seed)
    graph = RoadGraph()

    perturbation = main_spacing * (perturbation_pct / 100.0)

    # Layer 1: Main arterial grid
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
            graph.add_edge(nid, node_map[(i + 1, j)], width=14.0)
        if (i, j + 1) in node_map:
            graph.add_edge(nid, node_map[(i, j + 1)], width=14.0)

    # Layer 2: Secondary grid (uses sub_spacing)
    if sub_spacing > 0 and sub_spacing < main_spacing:
        sec_nodes = []
        sec_half = int(radius / sub_spacing) + 1
        sec_perturbation = sub_spacing * (perturbation_pct / 100.0) * 0.5
        for i in range(-sec_half, sec_half + 1):
            for j in range(-sec_half, sec_half + 1):
                # Skip if too close to main grid line
                ix = i * sub_spacing / main_spacing
                jy = j * sub_spacing / main_spacing
                if abs(ix - round(ix)) < 0.15 or abs(jy - round(jy)) < 0.15:
                    continue
                x = i * sub_spacing + rng.uniform(-sec_perturbation, sec_perturbation)
                y = j * sub_spacing + rng.uniform(-sec_perturbation, sec_perturbation)
                if x * x + y * y > radius ** 2:
                    continue
                nid = graph.add_node(x, y)
                sec_nodes.append((i, j, nid))

        sec_map = {}
        for i, j, nid in sec_nodes:
            sec_map[(i, j)] = nid

        for i, j, nid in sec_nodes:
            if (i + 1, j) in sec_map:
                graph.add_edge(nid, sec_map[(i + 1, j)], width=8.0)
            if (i, j + 1) in sec_map:
                graph.add_edge(nid, sec_map[(i, j + 1)], width=8.0)

    return _cleanup_graph(graph)


# ============================================================
# Mode 2: Radial + Ring (Paris / Moscow style)
# ============================================================
def _generate_radial_ring_road(radius, main_spacing, sub_spacing, perturbation_pct, seed):
    rng = random.Random(seed)
    graph = RoadGraph()

    n_rings = max(2, int(radius / main_spacing))
    n_radial = max(6, int(2 * math.pi * radius / main_spacing))

    # Rings (concentric circles)
    ring_nodes = []
    for ring_idx in range(1, n_rings + 1):
        r = ring_idx * (radius / n_rings)
        ring_nids = []
        for i in range(n_radial):
            angle = (2 * math.pi * i) / n_radial + rng.uniform(-0.05, 0.05)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            nid = graph.add_node(x, y)
            ring_nids.append(nid)
        # Connect ring
        for i in range(len(ring_nids)):
            graph.add_edge(ring_nids[i], ring_nids[(i + 1) % len(ring_nids)], width=12.0)
        ring_nodes.append(ring_nids)

    # Radial spokes
    for i in range(n_radial):
        spoke_nids = []
        for ring_idx in range(n_rings):
            nid = ring_nodes[ring_idx][i]
            spoke_nids.append(nid)
        for j in range(len(spoke_nids) - 1):
            graph.add_edge(spoke_nids[j], spoke_nids[j + 1], width=10.0)

    # Add some diagonal shortcuts between rings
    for ring_idx in range(n_rings - 1):
        for i in range(n_radial):
            if rng.random() < 0.15:
                j = (i + 1) % n_radial
                a = ring_nodes[ring_idx][i]
                b = ring_nodes[ring_idx + 1][j]
                graph.add_edge(a, b, width=6.0)

    return _cleanup_graph(graph)


# ============================================================
# Mode 3: Organic / L-System simplified
# ============================================================
def _generate_organic_road(radius, main_spacing, sub_spacing, perturbation_pct, seed):
    rng = random.Random(seed)
    graph = RoadGraph()

    # Seed roads from center outward
    n_seeds = max(4, rng.randint(4, 8))
    frontier = []

    for i in range(n_seeds):
        angle = (2 * math.pi * i) / n_seeds + rng.uniform(-0.3, 0.3)
        length = rng.uniform(radius * 0.3, radius * 0.8)
        x = length * math.cos(angle)
        y = length * math.sin(angle)
        nid = graph.add_node(x, y)
        frontier.append((nid, angle, length))

    # Branch and extend
    for _ in range(80):
        if not frontier:
            break
        parent_nid, parent_angle, parent_dist = frontier.pop(rng.randint(0, len(frontier) - 1))

        n_branches = rng.randint(1, 3)
        for _ in range(n_branches):
            branch_angle = parent_angle + rng.uniform(-math.pi / 3, math.pi / 3)
            branch_length = rng.uniform(main_spacing * 0.5, main_spacing * 1.2)
            if branch_length < sub_spacing:
                continue

            px, py = graph.nodes[parent_nid]
            x = px + branch_length * math.cos(branch_angle)
            y = py + branch_length * math.sin(branch_angle)

            if x * x + y * y > radius ** 2:
                continue

            # Avoid too-close nodes
            too_close = False
            for existing_nid, (ex, ey) in enumerate(graph.nodes):
                if (x - ex) ** 2 + (y - ey) ** 2 < (sub_spacing * 0.4) ** 2:
                    too_close = True
                    break
            if too_close:
                continue

            nid = graph.add_node(x, y)
            width = 10.0 if branch_length > main_spacing * 0.8 else 5.0
            graph.add_edge(parent_nid, nid, width=width)

            if branch_length > sub_spacing and x * x + y * y < (radius * 0.9) ** 2:
                frontier.append((nid, branch_angle, branch_length * 0.85))

    return _cleanup_graph(graph)


# ============================================================
# Mode 4: Mixed (Grid + Radial hybrid)
# ============================================================
def _generate_mixed_road(radius, main_spacing, sub_spacing, perturbation_pct, seed):
    rng = random.Random(seed)
    graph = RoadGraph()

    # Core: radial-ring near center
    inner_radius = radius * 0.35
    n_inner_rings = max(2, int(inner_radius / main_spacing))
    n_radial = max(6, int(2 * math.pi * inner_radius / main_spacing * 1.5))

    ring_nodes = []
    for ring_idx in range(1, n_inner_rings + 1):
        r = ring_idx * (inner_radius / n_inner_rings)
        ring_nids = []
        for i in range(n_radial):
            angle = (2 * math.pi * i) / n_radial + rng.uniform(-0.03, 0.03)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            nid = graph.add_node(x, y)
            ring_nids.append(nid)
        for i in range(len(ring_nids)):
            graph.add_edge(ring_nids[i], ring_nids[(i + 1) % len(ring_nids)], width=12.0)
        ring_nodes.append(ring_nids)

    for i in range(n_radial):
        for ring_idx in range(n_inner_rings - 1):
            graph.add_edge(ring_nodes[ring_idx][i], ring_nodes[ring_idx + 1][i], width=10.0)

    # Outer: grid extending radial spokes
    perturbation = main_spacing * (perturbation_pct / 100.0)
    outer_nodes = []
    outer_half = int(radius / main_spacing) + 1

    for i in range(-outer_half, outer_half + 1):
        for j in range(-outer_half, outer_half + 1):
            x = i * main_spacing + rng.uniform(-perturbation, perturbation)
            y = j * main_spacing + rng.uniform(-perturbation, perturbation)
            dist_sq = x * x + y * y
            if dist_sq < inner_radius ** 2 or dist_sq > (radius * 1.1) ** 2:
                continue
            nid = graph.add_node(x, y)
            outer_nodes.append((i, j, nid))

    outer_map = {}
    for i, j, nid in outer_nodes:
        outer_map[(i, j)] = nid

    for i, j, nid in outer_nodes:
        if (i + 1, j) in outer_map:
            graph.add_edge(nid, outer_map[(i + 1, j)], width=8.0)
        if (i, j + 1) in outer_map:
            graph.add_edge(nid, outer_map[(i, j + 1)], width=8.0)

    # Connect inner radial to outer grid
    for i in range(n_radial):
        angle = (2 * math.pi * i) / n_radial
        last_inner = ring_nodes[-1][i]
        # Find nearest outer node
        best_nid = None
        best_dist = float('inf')
        lx, ly = graph.nodes[last_inner]
        for _, _, onid in outer_nodes:
            ox, oy = graph.nodes[onid]
            d = (ox - lx) ** 2 + (oy - ly) ** 2
            if d < best_dist:
                best_dist = d
                best_nid = onid
        if best_nid and best_dist < (main_spacing * 1.5) ** 2:
            graph.add_edge(last_inner, best_nid, width=10.0)

    return _cleanup_graph(graph)
