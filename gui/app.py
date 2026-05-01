"""
Shortest Path Finder — GUI Application
CCC Algorithm Project
Built with Python Tkinter + Canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.dijkstra import dijkstra
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, reconstruct_path
from utils.graph import Graph


# ── Colour Palette ────────────────────────────────────────────────────────────
BG          = "#0f1117"
PANEL       = "#1a1d27"
CARD        = "#22263a"
ACCENT      = "#00d4aa"
ACCENT2     = "#ff6b6b"
ACCENT3     = "#ffd166"
TEXT        = "#e8eaf6"
TEXT_DIM    = "#7c83a0"
NODE_FILL   = "#2a2f47"
NODE_BORDER = "#00d4aa"
EDGE_COL    = "#3a3f5c"
PATH_COL    = "#00d4aa"
SOURCE_COL  = "#ffd166"
TARGET_COL  = "#ff6b6b"
VISITED_COL = "#7b5ea7"
FONT_HEAD   = ("Georgia", 13, "bold")
FONT_BODY   = ("Consolas", 10)
FONT_SMALL  = ("Consolas", 9)
FONT_NODE   = ("Georgia", 10, "bold")


# ── Preset Graphs ─────────────────────────────────────────────────────────────
PRESETS = {
    "Simple 6-Node": {
        "directed": False,
        "edges": [
            ("A","B",4),("A","D",2),("B","C",1),
            ("B","E",5),("C","F",3),("D","E",8),("E","F",2),
        ],
        "positions": {
            "A":(120,120),"B":(280,120),"C":(440,120),
            "D":(120,280),"E":(280,280),"F":(440,280),
        },
    },
    "City Network": {
        "directed": False,
        "edges": [
            ("NYC","BOS",215),("NYC","PHI",95),("NYC","DC",225),
            ("PHI","DC",140),("DC","RIC",110),("DC","PIT",245),
            ("PIT","CLV",130),("CLV","CHI",345),
        ],
        "positions": {
            "NYC":(300,100),"BOS":(440,80),"PHI":(260,180),
            "DC":(240,280),"RIC":(340,320),"PIT":(160,280),
            "CLV":(100,200),"CHI":(60,120),
        },
    },
    "Directed Graph": {
        "directed": True,
        "edges": [
            ("A","B",6),("A","C",7),("B","C",8),
            ("B","D",5),("B","E",-4),("C","D",-3),
            ("D","B",-2),("E","D",9),
        ],
        "positions": {
            "A":(160,200),"B":(280,120),"C":(280,280),
            "D":(400,200),"E":(400,320),
        },
    },
}


def reconstruct_from_pred(predecessors, source, target):
    path, node = [], target
    while node is not None:
        path.insert(0, node)
        node = predecessors.get(node)
    return path if path and path[0] == source else []


# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shortest Path Finder — CCC Algorithm Project")
        self.configure(bg=BG)
        self.geometry("1100x700")
        self.resizable(True, True)

        self.graph   = Graph(directed=False)
        self.node_pos = {}          # node → (x, y) on canvas
        self.path_nodes = []        # highlighted path
        self.visited_nodes = []
        self.result_text = ""

        self._drag_node = None
        self._adding_edge = False
        self._edge_src = None

        self._build_ui()
        self._load_preset("Simple 6-Node")

    # ── UI Layout ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ─ Top bar
        top = tk.Frame(self, bg=BG, pady=8)
        top.pack(fill="x", padx=16)
        tk.Label(top, text="◈  Shortest Path Finder",
                 font=("Georgia", 16, "bold"), bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(top, text="CCC Algorithm Project",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(side="left", padx=12)

        # ─ Main area
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=(0,12))

        # Left panel
        left = tk.Frame(main, bg=PANEL, width=260)
        left.pack(side="left", fill="y", padx=(0,10))
        left.pack_propagate(False)
        self._build_left(left)

        # Canvas
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_canvas(right)

    def _build_left(self, parent):
        def section(text):
            tk.Label(parent, text=text, font=FONT_HEAD,
                     bg=PANEL, fg=ACCENT).pack(anchor="w", padx=14, pady=(14,4))

        def sep():
            tk.Frame(parent, bg=CARD, height=1).pack(fill="x", padx=10, pady=4)

        # ── Preset
        section("① Load Preset Graph")
        self.preset_var = tk.StringVar(value="Simple 6-Node")
        cb = ttk.Combobox(parent, textvariable=self.preset_var,
                          values=list(PRESETS.keys()), state="readonly", width=26)
        cb.pack(padx=14, pady=4)
        self._btn(parent, "Load Preset", self._on_load_preset)

        sep()

        # ── Edit graph
        section("② Edit Graph")
        row = tk.Frame(parent, bg=PANEL)
        row.pack(padx=14, fill="x")
        self._btn(row, "+ Node", self._add_node, side="left")
        self._btn(row, "+ Edge", self._start_edge, side="left")

        row2 = tk.Frame(parent, bg=PANEL)
        row2.pack(padx=14, fill="x", pady=4)
        self._btn(row2, "✕ Clear", self._clear_graph, side="left")
        self.directed_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, text="Directed", variable=self.directed_var,
                       bg=PANEL, fg=TEXT, selectcolor=CARD,
                       activebackground=PANEL, font=FONT_SMALL,
                       command=self._toggle_directed).pack(side="left", padx=6)

        sep()

        # ── Algorithm
        section("③ Run Algorithm")
        tk.Label(parent, text="Source node:", bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", padx=14)
        self.source_var = tk.StringVar()
        self.source_cb = ttk.Combobox(parent, textvariable=self.source_var,
                                      state="readonly", width=26)
        self.source_cb.pack(padx=14, pady=2)

        tk.Label(parent, text="Target node (optional):", bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", padx=14)
        self.target_var = tk.StringVar()
        self.target_cb = ttk.Combobox(parent, textvariable=self.target_var,
                                      state="readonly", width=26)
        self.target_cb.pack(padx=14, pady=2)

        tk.Label(parent, text="Algorithm:", bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(6,0))
        self.algo_var = tk.StringVar(value="Dijkstra (Greedy)")
        for algo in ["Dijkstra (Greedy)", "Bellman-Ford (DP)", "Floyd-Warshall (DP)"]:
            tk.Radiobutton(parent, text=algo, variable=self.algo_var, value=algo,
                           bg=PANEL, fg=TEXT, selectcolor=CARD,
                           activebackground=PANEL, font=FONT_SMALL).pack(anchor="w", padx=20)

        self._btn(parent, "▶  Find Shortest Path", self._run_algo, color=ACCENT)

        sep()

        # ── Result box
        section("④ Result")
        self.result_box = tk.Text(parent, height=8, bg=CARD, fg=TEXT,
                                  font=FONT_SMALL, relief="flat",
                                  wrap="word", state="disabled",
                                  insertbackground=TEXT)
        self.result_box.pack(padx=14, pady=4, fill="x")

    def _btn(self, parent, text, cmd, side=None, color=None):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color or CARD, fg=TEXT if color else ACCENT,
                      font=FONT_SMALL, relief="flat", cursor="hand2",
                      activebackground=ACCENT, activeforeground=BG,
                      padx=8, pady=4)
        if side:
            b.pack(side=side, padx=3, pady=3)
        else:
            b.pack(padx=14, pady=4, fill="x")
        return b

    def _build_canvas(self, parent):
        tk.Label(parent, text="Graph Canvas  (drag nodes · double-click to delete)",
                 bg=BG, fg=TEXT_DIM, font=FONT_SMALL).pack(anchor="w")
        self.canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>",        self._canvas_click)
        self.canvas.bind("<B1-Motion>",       self._canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._canvas_release)
        self.canvas.bind("<Double-Button-1>", self._canvas_dbl)
        self.canvas.bind("<Configure>",       lambda e: self._draw())

    # ── Graph Drawing ──────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")
        if not self.node_pos:
            c.create_text(c.winfo_width()//2, c.winfo_height()//2,
                          text="Load a preset or add nodes to begin",
                          fill=TEXT_DIM, font=FONT_BODY)
            return

        # Draw edges
        drawn = set()
        for u, v, w in self.graph.get_edges():
            key = (min(u,v), max(u,v))
            if key in drawn and not self.graph.directed:
                continue
            drawn.add(key)

            x1,y1 = self.node_pos.get(u, (0,0))
            x2,y2 = self.node_pos.get(v, (0,0))

            on_path = self._edge_on_path(u, v)
            col = PATH_COL if on_path else EDGE_COL
            width = 3 if on_path else 1.5

            if self.graph.directed:
                self._draw_arrow(x1,y1,x2,y2,col,width,w)
            else:
                c.create_line(x1,y1,x2,y2, fill=col, width=width, smooth=True)
                mx, my = (x1+x2)//2, (y1+y2)//2
                c.create_text(mx, my-10, text=str(w),
                               fill=ACCENT3 if on_path else TEXT_DIM, font=FONT_SMALL)

        # Draw nodes
        R = 22
        for node, (x, y) in self.node_pos.items():
            if node in self.path_nodes:
                idx = self.path_nodes.index(node)
                if idx == 0:
                    fill, border = SOURCE_COL, SOURCE_COL
                elif idx == len(self.path_nodes)-1:
                    fill, border = TARGET_COL, TARGET_COL
                else:
                    fill, border = ACCENT, ACCENT
            elif node in self.visited_nodes:
                fill, border = VISITED_COL, VISITED_COL
            else:
                fill, border = NODE_FILL, NODE_BORDER

            # Glow effect
            if node in self.path_nodes:
                c.create_oval(x-R-5,y-R-5,x+R+5,y+R+5,
                              fill="", outline=border, width=1, stipple="gray25")

            c.create_oval(x-R,y-R,x+R,y+R,
                          fill=fill, outline=border, width=2)
            c.create_text(x, y, text=node,
                          fill=BG if node in self.path_nodes else TEXT,
                          font=FONT_NODE)

        # Legend
        items = [
            (SOURCE_COL, "Source"),
            (TARGET_COL, "Target"),
            (ACCENT,     "On Path"),
            (VISITED_COL,"Visited"),
        ]
        lx, ly = 12, c.winfo_height() - 20
        for col, label in items:
            c.create_oval(lx,ly-7,lx+14,ly+7, fill=col, outline="")
            c.create_text(lx+22, ly, text=label, fill=TEXT_DIM,
                          font=FONT_SMALL, anchor="w")
            lx += 90

        # Edge-adding hint
        if self._adding_edge and self._edge_src:
            c.create_text(c.winfo_width()//2, 18,
                          text=f"Now click target node  (source: {self._edge_src})",
                          fill=ACCENT3, font=FONT_BODY)

    def _draw_arrow(self, x1, y1, x2, y2, col, width, weight):
        c = self.canvas
        R = 22
        dx, dy = x2-x1, y2-y1
        dist = math.hypot(dx, dy) or 1
        ux, uy = dx/dist, dy/dist
        sx, sy = x1 + ux*R, y1 + uy*R
        ex, ey = x2 - ux*R, y2 - uy*R
        c.create_line(sx,sy,ex,ey, fill=col, width=width,
                      arrow=tk.LAST, arrowshape=(10,12,4))
        mx, my = (sx+ex)/2, (sy+ey)/2
        c.create_text(mx, my-10, text=str(weight),
                      fill=ACCENT3 if col==PATH_COL else TEXT_DIM, font=FONT_SMALL)

    def _edge_on_path(self, u, v):
        if len(self.path_nodes) < 2:
            return False
        for i in range(len(self.path_nodes)-1):
            a, b = self.path_nodes[i], self.path_nodes[i+1]
            if (a==u and b==v) or (not self.graph.directed and a==v and b==u):
                return True
        return False

    # ── Canvas Interaction ─────────────────────────────────────────────────────
    def _node_at(self, x, y, radius=26):
        for node, (nx, ny) in self.node_pos.items():
            if math.hypot(x-nx, y-ny) <= radius:
                return node
        return None

    def _canvas_click(self, e):
        if self._adding_edge:
            node = self._node_at(e.x, e.y)
            if node and self._edge_src:
                if node == self._edge_src:
                    return
                w = simpledialog.askstring("Edge Weight",
                    f"Weight for {self._edge_src} → {node}:",
                    initialvalue="1", parent=self)
                if w is None:
                    self._adding_edge = False
                    self._edge_src = None
                    self._draw()
                    return
                try:
                    weight = int(w)
                except ValueError:
                    messagebox.showerror("Error", "Weight must be an integer.")
                    return
                self.graph.add_edge(self._edge_src, node, weight)
                self._adding_edge = False
                self._edge_src = None
                self._update_node_combos()
                self._draw()
            elif node:
                self._edge_src = node
            return

        clicked = self._node_at(e.x, e.y)
        if clicked:
            self._drag_node = clicked
        else:
            self._drag_node = None

    def _canvas_drag(self, e):
        if self._drag_node and not self._adding_edge:
            self.node_pos[self._drag_node] = (e.x, e.y)
            self._draw()

    def _canvas_release(self, e):
        self._drag_node = None

    def _canvas_dbl(self, e):
        node = self._node_at(e.x, e.y)
        if node:
            if messagebox.askyesno("Delete Node", f"Delete node '{node}'?"):
                self.graph.remove_node(node)
                del self.node_pos[node]
                self.path_nodes = []
                self.visited_nodes = []
                self._update_node_combos()
                self._draw()

    # ── Graph Operations ───────────────────────────────────────────────────────
    def _add_node(self):
        name = simpledialog.askstring("Add Node", "Node name:", parent=self)
        if not name:
            return
        name = name.strip().upper()
        if self.graph.has_node(name):
            messagebox.showinfo("Info", f"Node '{name}' already exists.")
            return
        # Place near centre
        cx = self.canvas.winfo_width() // 2
        cy = self.canvas.winfo_height() // 2
        import random
        x = cx + random.randint(-120, 120)
        y = cy + random.randint(-100, 100)
        self.graph.add_node(name)
        self.node_pos[name] = (x, y)
        self._update_node_combos()
        self._draw()

    def _start_edge(self):
        if self.graph.node_count() < 2:
            messagebox.showinfo("Info", "Add at least 2 nodes first.")
            return
        self._adding_edge = True
        self._edge_src = None
        self._draw()
        messagebox.showinfo("Add Edge",
            "Click the SOURCE node, then the TARGET node on the canvas.")

    def _clear_graph(self):
        self.graph.clear()
        self.node_pos.clear()
        self.path_nodes = []
        self.visited_nodes = []
        self._update_node_combos()
        self._set_result("")
        self._draw()

    def _toggle_directed(self):
        self.graph.directed = self.directed_var.get()
        self._draw()

    def _load_preset(self, name):
        data = PRESETS[name]
        self.graph = Graph(directed=data["directed"])
        self.directed_var.set(data["directed"])
        self.node_pos = dict(data["positions"])
        for u, v, w in data["edges"]:
            self.graph.add_edge(u, v, w)
        self.path_nodes = []
        self.visited_nodes = []
        self._update_node_combos()
        self._set_result("")
        self.after(50, self._draw)

    def _on_load_preset(self):
        self._load_preset(self.preset_var.get())

    def _update_node_combos(self):
        nodes = self.graph.get_nodes()
        self.source_cb["values"] = nodes
        self.target_cb["values"] = ["(All)"] + nodes
        if nodes:
            if self.source_var.get() not in nodes:
                self.source_var.set(nodes[0])
            if self.target_var.get() not in nodes + ["(All)"]:
                self.target_var.set("(All)")
        else:
            self.source_var.set("")
            self.target_var.set("")

    # ── Run Algorithm ──────────────────────────────────────────────────────────
    def _run_algo(self):
        source = self.source_var.get().strip()
        target = self.target_var.get().strip()
        algo   = self.algo_var.get()

        if not source:
            messagebox.showwarning("Missing", "Please select a source node.")
            return
        if not self.graph.has_node(source):
            messagebox.showerror("Error", f"Node '{source}' not in graph.")
            return

        self.path_nodes   = []
        self.visited_nodes = []

        try:
            if "Dijkstra" in algo:
                dist, pred = dijkstra(self.graph, source)
                self._show_result("Dijkstra (Greedy)", source, target, dist, pred)

            elif "Bellman" in algo:
                res = bellman_ford(self.graph, source)
                if res is None:
                    self._set_result("⚠ Negative cycle detected!\nBellman-Ford cannot produce a valid result.")
                    self._draw()
                    return
                dist, pred = res
                self._show_result("Bellman-Ford (DP)", source, target, dist, pred)

            elif "Floyd" in algo:
                fw_dist, fw_nxt = floyd_warshall(self.graph)
                self._show_fw_result(source, target, fw_dist, fw_nxt)

        except Exception as ex:
            messagebox.showerror("Algorithm Error", str(ex))

        self._draw()

    def _show_result(self, algo_name, source, target, dist, pred):
        has_target = target and target != "(All)" and target != source
        lines = [f"Algorithm : {algo_name}", f"Source    : {source}", ""]

        if has_target:
            if target not in dist:
                self._set_result(f"Node '{target}' not in graph.")
                return
            d = dist[target]
            path = reconstruct_from_pred(pred, source, target)
            self.path_nodes = path
            self.visited_nodes = list(pred.keys())
            dist_str = str(d) if d != float('inf') else "∞ (unreachable)"
            lines += [
                f"Target    : {target}",
                f"Distance  : {dist_str}",
                f"Path      : {' → '.join(path) if path else 'No path'}",
            ]
        else:
            lines.append("All distances from source:")
            for n in sorted(dist):
                d = dist[n]
                ds = str(d) if d != float('inf') else "∞"
                path = reconstruct_from_pred(pred, source, n)
                lines.append(f"  {source}→{n}: {ds:>6}  [{' → '.join(path)}]")
            self.visited_nodes = list(pred.keys())

        self._set_result("\n".join(lines))

    def _show_fw_result(self, source, target, fw_dist, fw_nxt):
        has_target = target and target != "(All)" and target != source
        lines = ["Algorithm : Floyd-Warshall (DP)",
                 f"Source    : {source}", ""]
        if has_target:
            d = fw_dist.get(source, {}).get(target, float('inf'))
            path = reconstruct_path(fw_nxt, source, target)
            self.path_nodes = path
            dist_str = str(d) if d != float('inf') else "∞ (unreachable)"
            lines += [
                f"Target    : {target}",
                f"Distance  : {dist_str}",
                f"Path      : {' → '.join(path) if path else 'No path'}",
            ]
        else:
            lines.append("All-pairs distances (from source row):")
            for n in sorted(fw_dist.get(source, {})):
                d = fw_dist[source][n]
                ds = str(d) if d != float('inf') else "∞"
                path = reconstruct_path(fw_nxt, source, n)
                lines.append(f"  {source}→{n}: {ds:>6}  [{' → '.join(path)}]")
        self._set_result("\n".join(lines))

    def _set_result(self, text):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", text)
        self.result_box.config(state="disabled")


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
