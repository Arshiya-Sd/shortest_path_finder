"""
Dijkstra's Algorithm — Greedy
Finds shortest paths from source to all nodes (non-negative weights only).
Time: O((V+E) log V)  |  Space: O(V)
"""
import heapq


def dijkstra(graph, source):
    distances = {n: float('inf') for n in graph.get_nodes()}
    distances[source] = 0
    predecessors = {n: None for n in graph.get_nodes()}
    visited = set()
    pq = [(0, source)]

    while pq:
        dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph.get_neighbors(node):
            if neighbor in visited:
                continue
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))

    return distances, predecessors
