"""
Graph Data Structure
Supports directed and undirected weighted graphs.
"""


class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self._adjacency = {}
        self._edges = []

    def add_node(self, node):
        if node not in self._adjacency:
            self._adjacency[node] = []

    def add_edge(self, u, v, weight=1):
        self.add_node(u)
        self.add_node(v)
        self._adjacency[u].append((v, weight))
        self._edges.append((u, v, weight))
        if not self.directed:
            self._adjacency[v].append((u, weight))

    def remove_node(self, node):
        if node in self._adjacency:
            del self._adjacency[node]
        self._edges = [(u, v, w) for u, v, w in self._edges if u != node and v != node]
        for n in self._adjacency:
            self._adjacency[n] = [(nb, w) for nb, w in self._adjacency[n] if nb != node]

    def remove_edge(self, u, v):
        self._edges = [(a, b, w) for a, b, w in self._edges if not (a == u and b == v)]
        self._adjacency[u] = [(nb, w) for nb, w in self._adjacency[u] if nb != v]
        if not self.directed:
            self._adjacency[v] = [(nb, w) for nb, w in self._adjacency[v] if nb != u]

    def clear(self):
        self._adjacency = {}
        self._edges = []

    def get_nodes(self):
        return sorted(self._adjacency.keys())

    def get_edges(self):
        return self._edges

    def get_neighbors(self, node):
        return self._adjacency.get(node, [])

    def node_count(self):
        return len(self._adjacency)

    def edge_count(self):
        return len(self._edges)

    def has_node(self, node):
        return node in self._adjacency

    def has_edge(self, u, v):
        return any(a == u and b == v for a, b, _ in self._edges)
