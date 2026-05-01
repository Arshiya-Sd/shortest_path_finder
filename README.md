# 🗺️ Shortest Path Finder

> **CCC Algorithm Project** — A GUI-based application that visualises and compares three shortest-path algorithms: Dijkstra's (Greedy), Bellman-Ford (Dynamic Programming), and Floyd-Warshall (Dynamic Programming).

---

## 📋 Project Report

### 1. Introduction

Finding the shortest path between two points is one of the most fundamental problems in computer science and real-world applications. Whether it is navigation systems (Google Maps), network routing protocols (OSPF), or game AI pathfinding — shortest path algorithms are everywhere.

This project implements and visually demonstrates three well-known shortest path algorithms on an interactive graph, allowing users to build their own graphs, load preset graphs, choose an algorithm, and see the shortest path highlighted in real time.

---

### 2. Problem Statement

Given a **weighted graph** G = (V, E) and a **source node** s, find the shortest (minimum cost) path from s to every other node — or between all pairs of nodes. The project handles:

- Non-negative weights (Dijkstra)
- Negative weights (Bellman-Ford, Floyd-Warshall)
- Single-source and all-pairs variants
- Negative cycle detection

---

### 3. Algorithms Implemented

#### 3.1 Dijkstra's Algorithm — Greedy

**Classification:** Greedy Algorithm

Dijkstra's algorithm is a classic **greedy** approach. At every step, it greedily selects the unvisited node with the smallest known tentative distance and "settles" it permanently.

**Why is it Greedy?**
The greedy choice property holds because all edge weights are non-negative: once we settle a node, no future path through an unsettled node can improve its distance. We commit locally to the best-known option at each step, and this local optimum always leads to a globally optimal solution.

**Algorithm Steps:**
```
1. Set dist[source] = 0, dist[all others] = ∞
2. Push (0, source) into a min-heap priority queue
3. While the heap is not empty:
   a. Pop the node u with minimum distance  ← GREEDY CHOICE
   b. For each neighbour v of u:
      - new_dist = dist[u] + weight(u, v)
      - If new_dist < dist[v]:
          dist[v] = new_dist
          predecessors[v] = u
          Push (new_dist, v) into heap
4. Return dist[], predecessors[]
```

**Complexity:**
| | Value |
|---|---|
| Time | O((V + E) log V) |
| Space | O(V) |

**Limitation:** Cannot handle negative edge weights.

---

#### 3.2 Bellman-Ford Algorithm — Dynamic Programming

**Classification:** Dynamic Programming

Bellman-Ford uses a **bottom-up DP** strategy. The sub-problem is:

> *"What is the shortest path from source to node v using at most k edges?"*

**DP Recurrence:**
```
dist[v][k] = min(dist[v][k-1],  min over all edges (u,v) of dist[u][k-1] + w(u,v))
```

We iterate this V−1 times (since any shortest path in a graph with V nodes uses at most V−1 edges), building up the solution from paths of length 1 to length V−1.

**Algorithm Steps:**
```
1. Set dist[source] = 0, dist[all others] = ∞
2. Repeat V-1 times:
   For every edge (u, v, w):
       If dist[u] + w < dist[v]:
           dist[v] = dist[u] + w    ← DP relaxation
3. Negative cycle check:
   For every edge (u, v, w):
       If dist[u] + w < dist[v]: NEGATIVE CYCLE DETECTED
```

**Complexity:**
| | Value |
|---|---|
| Time | O(V × E) |
| Space | O(V) |

**Advantage over Dijkstra:** Handles negative edge weights and detects negative cycles.

---

#### 3.3 Floyd-Warshall Algorithm — Dynamic Programming

**Classification:** Dynamic Programming

Floyd-Warshall solves the **all-pairs shortest path** problem using a 2D DP table.

**Sub-problem definition:**
> *"What is the shortest path from node i to node j, using only nodes {1, 2, ..., k} as intermediate nodes?"*

**DP Recurrence:**
```
dist[i][j][k] = min(
    dist[i][j][k-1],                      — don't use node k as intermediate
    dist[i][k][k-1] + dist[k][j][k-1]    — route through k
)
```

The key insight: for each intermediate node k we ask "can we improve the i→j path by going through k?" Three nested loops over all (i, k, j) triples give us all-pairs shortest paths.

**Algorithm Steps:**
```
1. Initialise dist[i][j] = weight of direct edge, or ∞ if none
2. Set dist[i][i] = 0 for all i
3. For k in all nodes:
     For i in all nodes:
       For j in all nodes:
         if dist[i][k] + dist[k][j] < dist[i][j]:
           dist[i][j] = dist[i][k] + dist[k][j]
           next[i][j] = next[i][k]
```

**Complexity:**
| | Value |
|---|---|
| Time | O(V³) |
| Space | O(V²) |

**Advantage:** Computes shortest paths between ALL pairs in one run.

---

### 4. Comparison Table

| Feature | Dijkstra | Bellman-Ford | Floyd-Warshall |
|---|---|---|---|
| Algorithm Type | **Greedy** | **Dynamic Programming** | **Dynamic Programming** |
| Negative Weights | ❌ No | ✅ Yes | ✅ Yes |
| Negative Cycle Detection | ❌ No | ✅ Yes | ✅ Yes |
| Single Source | ✅ Yes | ✅ Yes | ❌ (All-pairs) |
| All Pairs | ❌ No | ❌ No | ✅ Yes |
| Time Complexity | O((V+E) log V) | O(V×E) | O(V³) |
| Space Complexity | O(V) | O(V) | O(V²) |
| Best For | Dense graphs, non-neg weights | Graphs with neg weights | All-pairs on small graphs |

---

### 5. System Design

#### 5.1 Architecture

```
shortest_path_finder/
│
├── main.py                    ← Launch point
│
├── algorithms/
│   ├── dijkstra.py            ← Greedy: Dijkstra
│   ├── bellman_ford.py        ← DP: Bellman-Ford
│   └── floyd_warshall.py      ← DP: Floyd-Warshall
│
├── gui/
│   └── app.py                 ← Tkinter GUI + Canvas visualiser
│
├── utils/
│   └── graph.py               ← Graph data structure (adjacency list)
│
└── tests/
    └── test_all.py            ← Unit & integration tests
```

#### 5.2 Data Structure — Graph

The graph is represented using an **adjacency list** (`dict` of lists), which is efficient for sparse graphs:

- `add_node(n)` — O(1)
- `add_edge(u, v, w)` — O(1)
- `get_neighbors(n)` — O(degree(n))
- `get_edges()` — O(E)

Both directed and undirected graphs are supported.

#### 5.3 GUI Features

- **Canvas-based graph visualisation** — nodes and edges drawn with Tkinter Canvas
- **Drag-and-drop nodes** — reposition nodes by clicking and dragging
- **Add nodes/edges interactively** — click buttons, then click on canvas
- **Delete nodes** — double-click any node
- **Preset graphs** — load ready-made graphs (Simple 6-Node, City Network, Directed)
- **Algorithm selector** — choose Dijkstra, Bellman-Ford, or Floyd-Warshall
- **Source & target selection** — dropdown menus for start/end nodes
- **Path highlighting** — shortest path shown in teal, source in yellow, target in red
- **Result panel** — displays distances and full path

---

### 6. Sample Output

**Graph:**
```
    A --4-- B --1-- C
    |       |       |
    2       5       3
    |       |       |
    D --8-- E --2-- F
```

**Shortest paths from A (all algorithms agree):**
```
A → A :  0   [A]
A → B :  4   [A → B]
A → C :  5   [A → B → C]
A → D :  2   [A → D]
A → E :  9   [A → B → C → F → E]
A → F :  8   [A → B → C → F]
```

---

### 7. How to Run

#### Requirements
- Python 3.7 or higher
- `tkinter` (bundled with Python on Windows/macOS; on Linux: `sudo apt install python3-tk`)
- No third-party packages needed

#### Launch GUI
```bash
python main.py
```

#### Run Tests
```bash
python tests/test_all.py
```

---

### 8. Key Learnings

- **Greedy vs DP:** Dijkstra's greedy choice works because non-negative weights guarantee no future path can improve a settled node. Bellman-Ford's DP relaxation works even with negative weights by considering all possible path lengths systematically.
- **Optimal substructure:** All three algorithms rely on the fact that subpaths of shortest paths are themselves shortest paths — a classic DP/Greedy property.
- **Trade-offs:** Dijkstra is fastest for non-negative graphs; Bellman-Ford is more general; Floyd-Warshall is best when all-pairs results are needed at once.

---

### 9. References

1. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. — *Introduction to Algorithms*, 3rd Edition (CLRS)
2. Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs." *Numerische Mathematik*, 1, 269–271.
3. Bellman, R. (1958). "On a routing problem." *Quarterly of Applied Mathematics*, 16(1), 87–90.
4. Floyd, R. W. (1962). "Algorithm 97: Shortest Path." *Communications of the ACM*, 5(6), 345.
5. Python Software Foundation — *tkinter documentation*. https://docs.python.org/3/library/tkinter.html

---

*Submitted to CCC as part of the Algorithm Project requirement.*
*Demonstrates: Greedy Algorithm (Dijkstra) and Dynamic Programming (Bellman-Ford, Floyd-Warshall)*

---

**Author:** Mukkapati Daa Venkata Kirthika
**GitHub:** [kirthika-5656](https://github.com/kirthika-5656)
