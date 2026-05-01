"""
Bellman-Ford Algorithm — Dynamic Programming
Finds shortest paths; handles negative weights; detects negative cycles.
Time: O(V × E)  |  Space: O(V)
"""


def bellman_ford(graph, source):
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    V = len(nodes)

    distances = {n: float('inf') for n in nodes}
    distances[source] = 0
    predecessors = {n: None for n in nodes}

    for _ in range(V - 1):
        updated = False
        for u, v, w in edges:
            if distances[u] != float('inf') and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u
                updated = True
        if not updated:
            break

    # Negative cycle check
    for u, v, w in edges:
        if distances[u] != float('inf') and distances[u] + w < distances[v]:
            return None  # Negative cycle

    return distances, predecessors
