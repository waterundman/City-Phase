import math
from ..utils.geo_utils import polygon_area, polygon_centroid


def extract_blocks_from_graph(graph):
    blocks = []

    def find_cycles():
        visited_edges = set()
        cycles = []
        seen_cycle_keys = set()

        for start_node in range(graph.node_count()):
            if len(graph.adj.get(start_node, set())) < 2:
                continue

            for start_neighbor in sorted(graph.adj.get(start_node, set())):
                edge_key = tuple(sorted((start_node, start_neighbor)))
                if edge_key in visited_edges:
                    continue

                path = [start_node, start_neighbor]
                path_edges = {edge_key}

                current = start_neighbor
                prev = start_node

                max_steps = graph.node_count() * 3
                steps = 0
                while current != start_node and steps < max_steps:
                    steps += 1
                    neighbors = sorted(graph.adj.get(current, set()))
                    best_next = None
                    best_angle = -math.pi

                    cx, cy = graph.nodes[current]
                    px, py = graph.nodes[prev]
                    incoming_angle = math.atan2(cy - py, cx - px)

                    for nb in neighbors:
                        if nb == prev:
                            continue
                        edge_k = tuple(sorted((current, nb)))
                        if edge_k in path_edges:
                            continue

                        nx, ny = graph.nodes[nb]
                        edge_angle = math.atan2(ny - cy, nx - cx)
                        turn_angle = edge_angle - incoming_angle
                        while turn_angle > math.pi:
                            turn_angle -= 2 * math.pi
                        while turn_angle < -math.pi:
                            turn_angle += 2 * math.pi

                        right_turn = -turn_angle
                        if right_turn > best_angle:
                            best_angle = right_turn
                            best_next = nb

                    if best_next is None:
                        break

                    edge_k = tuple(sorted((current, best_next)))
                    path_edges.add(edge_k)
                    path.append(best_next)
                    prev = current
                    current = best_next

                if current == start_node and len(path) >= 3:
                    cycle_key = _canonical_cycle(path)
                    if cycle_key not in seen_cycle_keys:
                        seen_cycle_keys.add(cycle_key)
                        cycles.append(path)
                        for edge_idx in range(len(path) - 1):
                            ek = tuple(sorted((path[edge_idx], path[edge_idx + 1])))
                            visited_edges.add(ek)
                        ek = tuple(sorted((path[-1], path[0])))
                        visited_edges.add(ek)

        return cycles

    cycles = find_cycles()

    for cycle in cycles:
        polygon = [graph.nodes[nid] for nid in cycle]
        if len(polygon) >= 3:
            area = abs(polygon_area(polygon))
            if area > 100:
                blocks.append({
                    "polygon": polygon,
                    "area": area,
                    "center": polygon_centroid(polygon),
                })

    return blocks


def _canonical_cycle(path):
    min_val = min(path)
    min_idx = path.index(min_val)
    rotated = path[min_idx:] + path[:min_idx]
    reversed_path = [rotated[0]] + rotated[1:][::-1]
    return tuple(rotated) if tuple(rotated) < tuple(reversed_path) else tuple(reversed_path)
