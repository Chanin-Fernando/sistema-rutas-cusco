import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import math
import time
from ..data import generar_pedidos, generar_repartidores, construir_grafo, NODOS
from ..models import Pedido, Repartidor
from ..algorithms import (
    OrdenacionBusqueda,
    AlgoritmoGreedy,
    DivideYVenceras,
    ProgramacionDinamica,
    Backtracking
)
from .tabs import (
    DatosTab,
    OrdenacionTab,
    GreedyTab,
    DivideTab,
    PDTab,
    BacktrackingTab
)

class AppCusco(tk.Tk):
    COLORES = {
        "bg":        "#1a1a2e",
        "panel":     "#16213e",
        "card":      "#0f3460",
        "accent":    "#e94560",
        "accent2":   "#f5a623",
        "text":      "#eaeaea",
        "text2":     "#a0a8b0",
        "success":   "#4caf50",
        "warning":   "#ff9800",
        "info":      "#2196f3",
        "border":    "#253d5b",
    }

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Rutas Óptimas – Cusco")
        self.geometry("1400x820")
        self.configure(bg=self.COLORES["bg"])
        self.resizable(True, True)

        self.pedidos = generar_pedidos(12)
        self.repartidores = generar_repartidores()

        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        c = self.COLORES

        style.configure("TNotebook", background=c["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
            background=c["panel"], foreground=c["text2"],
            padding=[18, 8], font=("Courier New", 10, "bold"))
        style.map("TNotebook.Tab",
            background=[("selected", c["card"])],
            foreground=[("selected", c["accent"])])
        style.configure("Treeview",
            background=c["panel"], foreground=c["text"],
            fieldbackground=c["panel"], rowheight=26,
            font=("Courier New", 9))
        style.configure("Treeview.Heading",
            background=c["card"], foreground=c["accent"],
            font=("Courier New", 9, "bold"))
        style.map("Treeview",
            background=[("selected", c["accent"])],
            foreground=[("selected", "white")])
        style.configure("TCombobox",
            fieldbackground=c["panel"], background=c["panel"],
            foreground=c["text"], selectbackground=c["card"])

    def _construir_ui(self):
        c = self.COLORES
        header = tk.Frame(self, bg=c["card"], height=55)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header,
            text="  🗺  SISTEMA DE RUTAS ÓPTIMAS – CUSCO",
            bg=c["card"], fg=c["accent"],
            font=("Courier New", 15, "bold")
        ).pack(side=tk.LEFT, padx=15, pady=10)
        tk.Label(header,
            text="UNSAAC · Programación III · 2026",
            bg=c["card"], fg=c["text2"],
            font=("Courier New", 9)
        ).pack(side=tk.RIGHT, padx=20, pady=18)

        body = tk.Frame(self, bg=c["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Frame del mapa (izquierda)
        mapa_frame = tk.Frame(body, bg=c["panel"],
                               bd=1, relief=tk.FLAT,
                               highlightbackground=c["border"],
                               highlightthickness=1)
        mapa_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False,
                        padx=(0, 6))
        mapa_frame.configure(width=440)
        mapa_frame.pack_propagate(False)

        tk.Label(mapa_frame, text="MAPA DE CUSCO",
                 bg=c["panel"], fg=c["accent"],
                 font=("Courier New", 10, "bold")).pack(pady=(8, 2))

        self.canvas_mapa = tk.Canvas(mapa_frame,
            bg="#0d1b2a", width=420, height=420,
            highlightthickness=0)
        self.canvas_mapa.pack(padx=10, pady=5)
        self._dibujar_mapa()

        self.lbl_mapa_info = tk.Label(mapa_frame,
            text="Haz clic en una pestaña para visualizar el resultado",
            bg=c["panel"], fg=c["text2"],
            font=("Courier New", 8), wraplength=400, justify=tk.LEFT)
        self.lbl_mapa_info.pack(padx=10, pady=4)

        # Tabs de algoritmos (derecha)
        tabs_frame = tk.Frame(body, bg=c["bg"])
        tabs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        nb = ttk.Notebook(tabs_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # Instanciar cada tab, pasando la referencia a la app
        self.tab_datos = DatosTab(nb, self)
        self.tab_ordenacion = OrdenacionTab(nb, self)
        self.tab_greedy = GreedyTab(nb, self)
        self.tab_divide = DivideTab(nb, self)
        self.tab_pd = PDTab(nb, self)
        self.tab_backtracking = BacktrackingTab(nb, self)

    def _dibujar_mapa(self, ruta_resaltada: list = None,
                       pedidos_resaltados: list = None,
                       cuadrantes: list = None):
        cv = self.canvas_mapa
        cv.delete("all")
        c = self.COLORES
        W, H = 420, 420
        MARGEN = 30

        def to_px(x, y):
            px = MARGEN + (x / 100) * (W - 2 * MARGEN)
            py = H - MARGEN - (y / 100) * (H - 2 * MARGEN)
            return px, py

        # Cuadrícula
        for i in range(0, 101, 10):
            gx, _ = to_px(i, 0)
            _, gy = to_px(0, i)
            cv.create_line(gx, MARGEN, gx, H - MARGEN, fill="#1a2a3a", width=1)
            cv.create_line(MARGEN, gy, W - MARGEN, gy, fill="#1a2a3a", width=1)

        # Cuadrantes
        if cuadrantes:
            quad_colors = ["#1e3a5f", "#1a3d2e", "#3d2a1a", "#3d1a2a"]
            for idx, quad in enumerate(cuadrantes):
                bnd = quad["bounds"]
                x1, y1 = to_px(bnd[0], bnd[3])
                x2, y2 = to_px(bnd[1], bnd[2])
                cv.create_rectangle(x1, y1, x2, y2,
                    fill=quad_colors[idx % len(quad_colors)],
                    outline="#3a5f7a", width=1, stipple="gray25")

        # Aristas
        grafo = construir_grafo()
        aristas_dibujadas = set()
        for nodo_a, vecinos in grafo.items():
            for nodo_b, peso in vecinos:
                key = tuple(sorted([nodo_a, nodo_b]))
                if key in aristas_dibujadas:
                    continue
                aristas_dibujadas.add(key)
                en_ruta = False
                if ruta_resaltada and len(ruta_resaltada) > 1:
                    for i in range(len(ruta_resaltada) - 1):
                        if ({ruta_resaltada[i], ruta_resaltada[i+1]} ==
                                {nodo_a, nodo_b}):
                            en_ruta = True
                            break
                ax, ay = to_px(*NODOS[nodo_a])
                bx, by = to_px(*NODOS[nodo_b])
                color = c["accent"] if en_ruta else "#2a4a6a"
                width = 3 if en_ruta else 1
                cv.create_line(ax, ay, bx, by, fill=color, width=width)
                mx, my = (ax + bx) / 2, (ay + by) / 2
                cv.create_text(mx, my, text=str(peso),
                               fill="#3a6a8a", font=("Courier New", 7))

        # Nodos
        for nombre, (nx, ny) in NODOS.items():
            px, py = to_px(nx, ny)
            en_ruta = ruta_resaltada and nombre in ruta_resaltada
            color_nodo = c["accent"] if en_ruta else c["info"]
            r = 8 if en_ruta else 6
            cv.create_oval(px - r, py - r, px + r, py + r,
                           fill=color_nodo, outline="white", width=1)
            cv.create_text(px, py - 14, text=nombre,
                           fill="white" if en_ruta else c["text2"],
                           font=("Courier New", 7,
                                 "bold" if en_ruta else "normal"),
                           anchor=tk.CENTER)

        # Pedidos
        if pedidos_resaltados:
            PRIO_COLS = {1: c["accent"], 2: c["warning"], 3: c["success"]}
            for p in pedidos_resaltados:
                px, py = to_px(p.coord_x, p.coord_y)
                col = PRIO_COLS.get(p.prioridad, "white")
                cv.create_polygon(
                    px, py - 8,
                    px + 6, py + 4,
                    px - 6, py + 4,
                    fill=col, outline="white", width=1
                )
                cv.create_text(px, py - 16, text=f"#{p.id}",
                               fill=col, font=("Courier New", 7, "bold"))

        # Repartidores
        for rep in self.repartidores:
            rx, ry = to_px(rep.pos_x, rep.pos_y)
            cv.create_rectangle(rx - 6, ry - 6, rx + 6, ry + 6,
                                 fill=c["accent2"], outline="white", width=1)
            cv.create_text(rx, ry - 14, text=rep.nombre[:3],
                           fill=c["accent2"], font=("Courier New", 7, "bold"))

        # Leyenda
        leyenda = [
            (c["info"],    "Nodo del mapa"),
            (c["accent"],  "Ruta seleccionada"),
            (c["accent"],  "Pedido urgente"),
            (c["warning"], "Pedido normal"),
            (c["accent2"], "Repartidor"),
        ]
        for i, (col, txt) in enumerate(leyenda):
            cv.create_rectangle(8, 8 + i * 14, 18, 18 + i * 14,
                                 fill=col, outline="")
            cv.create_text(22, 13 + i * 14, text=txt, anchor=tk.W,
                           fill=c["text2"], font=("Courier New", 7))

    # Métodos auxiliares para que los tabs puedan actualizar el mapa
    def actualizar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        self._dibujar_mapa(ruta_resaltada, pedidos_resaltados, cuadrantes)

    def set_info_mapa(self, texto):
        self.lbl_mapa_info.config(text=texto)