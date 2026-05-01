"""
Test Suite — Shortest Path Finder
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.dijkstra import dijkstra
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, reconstruct_path
from utils.graph import Graph

P, F = "PASS", "FAIL"

def chk(name, expected, actual):
    ok = expected == actual
    print(f"  {'✓' if ok else '✗'} {name}")
    if not ok:
        print(f"    Expected: {expected}  Got: {actual}")
    return ok

def build_sample():
    g = Graph(directed=False)
    for u,v,w in [("A","B",4),("A","D",2),("B","C",1),
                  ("B","E",5),("C","F",3),("D","E",8),("E","F",2)]:
        g.add_edge(u,v,w)
    return g

def test_dijkstra():
    print("\n[Dijkstra]")
    g = build_sample()
    d, p = dijkstra(g, "A")
    return all([chk("A→A=0",0,d["A"]), chk("A→B=4",4,d["B"]),
                chk("A→C=5",5,d["C"]), chk("A→F=8",8,d["F"]),
                chk("A→D=2",2,d["D"]), chk("A→E=9",9,d["E"])])

def test_bellman_ford():
    print("\n[Bellman-Ford]")
    g = build_sample()
    r = bellman_ford(g, "A")
    assert r is not None
    d, _ = r
    ok = all([chk("A→F=8",8,d["F"]), chk("A→D=2",2,d["D"])])

    # Negative weights
    g2 = Graph(directed=True)
    for u,v,w in [("A","B",4),("A","C",2),("B","C",-3),("B","D",5),("C","D",1)]:
        g2.add_edge(u,v,w)
    r2 = bellman_ford(g2, "A")
    assert r2 is not None
    d2,_ = r2
    ok = ok and chk("neg edge A→C=1",1,d2["C"])

    # Negative cycle
    g3 = Graph(directed=True)
    for u,v,w in [("A","B",1),("B","C",-2),("C","A",-1)]:
        g3.add_edge(u,v,w)
    ok = ok and chk("neg cycle=None",None,bellman_ford(g3,"A"))
    return ok

def test_floyd_warshall():
    print("\n[Floyd-Warshall]")
    g = build_sample()
    dist, nxt = floyd_warshall(g)
    path = reconstruct_path(nxt,"A","F")
    return all([chk("A→F=8",8,dist["A"]["F"]),
                chk("F→A=8",8,dist["F"]["A"]),
                chk("self A=0",0,dist["A"]["A"]),
                chk("path starts A","A",path[0] if path else None),
                chk("path ends F","F",path[-1] if path else None)])

def test_agreement():
    print("\n[Cross-Algorithm Agreement]")
    g = build_sample()
    d_d,_ = dijkstra(g,"A")
    bf_d,_ = bellman_ford(g,"A")
    fw_d,_ = floyd_warshall(g)
    ok = True
    for n in g.get_nodes():
        same = d_d[n]==bf_d[n]==fw_d["A"][n]
        ok = ok and chk(f"A→{n} agree",True,same)
    return ok

def run_all_tests():
    print("="*50)
    print("  RUNNING ALL TESTS")
    print("="*50)
    tests = [test_dijkstra, test_bellman_ford, test_floyd_warshall, test_agreement]
    passed = sum(1 for t in tests if t())
    print(f"\n{'='*50}")
    print(f"  {passed}/{len(tests)} test groups passed")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
