"""
Floyd-Warshall Algorithm — Dynamic Programming
All-pairs shortest paths. Handles negative weights (not cycles).
Time: O(V³)  |  Space: O(V²)
"""


def floyd_warshall(graph):
    nodes = graph.get_nodes()
    dist = {i: {j: float('inf') for j in nodes} for i in nodes}
    nxt = {i: {j: None for j in nodes} for i in nodes}

    for n in nodes:
        dist[n][n] = 0

    for u, v, w in graph.get_edges():
        if w < dist[u][v]:
            dist[u][v] = w
            nxt[u][v] = v
        if not graph.directed and w < dist[v][u]:
            dist[v][u] = w
            nxt[v][u] = u

    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    for n in nodes:
        if dist[n][n] < 0:
            raise ValueError("Negative cycle detected")

    return dist, nxt


def reconstruct_path(nxt, source, target):
    if nxt[source][target] is None:
        return []
    path = [source]
    while source != target:
        source = nxt[source][target]
        if source is None:
            return []
        path.append(source)
    return path
