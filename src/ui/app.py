import tkinter as tk
from tkinter import ttk, font as tkfont
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

# ─── Paleta Google Maps Light ─────────────────────────────────────────────────
C = {
    "map_bg":       "#e8e0d8",   # fondo del mapa (beige calles)
    "map_road":     "#ffffff",   # calles principales
    "map_road2":    "#f5e9c6",   # calles secundarias
    "map_water":    "#a8d4f0",   # agua (no se usa pero referencia)
    "map_park":     "#c8e6c9",   # parques
    "panel_bg":     "#ffffff",   # panel lateral blanco
    "panel_border": "#e0e0e0",   # borde panel
    "topbar_bg":    "#ffffff",   # barra superior
    "accent":       "#1a73e8",   # azul Google
    "accent_dark":  "#1557b0",
    "accent2":      "#34a853",   # verde Google
    "red":          "#ea4335",   # rojo Google
    "yellow":       "#fbbc04",   # amarillo Google
    "text":         "#202124",   # texto principal
    "text2":        "#5f6368",   # texto secundario
    "text3":        "#80868b",   # placeholder
    "chip_bg":      "#f1f3f4",   # fondo chips/botones
    "chip_hover":   "#e8eaed",
    "route_blue":   "#4285f4",   # ruta azul
    "route_stroke": "#1a56d6",
    "node_fill":    "#4285f4",
    "node_sel":     "#ea4335",
    "shadow":       "#cccccc",
    "success":      "#34a853",
    "warning":      "#fbbc04",
    "danger":       "#ea4335",
    "info":         "#1a73e8",
    "separator":    "#f1f3f4",
    "tag_green":    "#e6f4ea",
    "tag_green_t":  "#137333",
    "tag_blue":     "#e8f0fe",
    "tag_blue_t":   "#1a73e8",
    "tag_red":      "#fce8e6",
    "tag_red_t":    "#c5221f",
}

ALGO_TABS = [
    ("📦 Datos",          "datos"),
    ("🔢 Ordenación",     "ordenacion"),
    ("⚡ Greedy",         "greedy"),
    ("🗺 Divide",         "divide"),
    ("💼 P. Dinámica",    "pd"),
    ("🔙 Backtracking",   "backtracking"),
]


class AppCusco(tk.Tk):
    # Exponer paleta para que los tabs la usen
    COLORES = C

    def __init__(self):
        super().__init__()
        self.title("Rutas Óptimas – Cusco")
        self.geometry("1380x800")
        self.minsize(1100, 650)
        self.configure(bg=C["panel_bg"])
        self.resizable(True, True)

        self.pedidos = generar_pedidos(12)
        self.repartidores = generar_repartidores()

        self._tab_index = 0          # índice de la pestaña activa
        self._tab_frames = []        # frames de contenido de cada tab
        self._tab_buttons = []       # botones del sidebar

        self._configurar_estilos()
        self._construir_ui()

    # ─── Estilos ttk ──────────────────────────────────────────────────────────
    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
            background=C["panel_bg"], foreground=C["text"],
            fieldbackground=C["panel_bg"], rowheight=28,
            font=("Segoe UI", 9), borderwidth=0)
        style.configure("Treeview.Heading",
            background=C["separator"], foreground=C["text2"],
            font=("Segoe UI", 9, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview",
            background=[("selected", C["tag_blue"])],
            foreground=[("selected", C["accent"])])
        style.configure("TCombobox",
            fieldbackground=C["chip_bg"], background=C["chip_bg"],
            foreground=C["text"], selectbackground=C["tag_blue"],
            relief="flat", borderwidth=1)
        style.map("TCombobox", fieldbackground=[("readonly", C["chip_bg"])])
        style.configure("TScrollbar",
            background=C["chip_bg"], troughcolor=C["separator"],
            relief="flat", borderwidth=0, arrowsize=12)

    # ─── Layout principal ─────────────────────────────────────────────────────
    def _construir_ui(self):
        # ── Barra superior tipo Google Maps ──
        self._build_topbar()

        # ── Cuerpo: sidebar izquierdo + mapa derecho ──
        body = tk.Frame(self, bg=C["separator"])
        body.pack(fill=tk.BOTH, expand=True)

        # Mapa primero (ocupa el resto) — debe existir antes de que los tabs llamen actualizar_mapa
        self.mapa_frame = tk.Frame(body, bg=C["map_bg"])
        self.mapa_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_mapa()

        # Separador
        tk.Frame(body, bg=C["panel_border"], width=1).pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar (se construye después, cuando canvas_mapa ya existe)
        self.sidebar = tk.Frame(body, bg=C["panel_bg"], width=380)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

    # ─── Barra superior ───────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["topbar_bg"], height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        # Logo / título
        logo_frame = tk.Frame(bar, bg=C["topbar_bg"])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=8)
        tk.Label(logo_frame, text="🗺", bg=C["topbar_bg"],
                 font=("Segoe UI", 20)).pack(side=tk.LEFT)
        title_frame = tk.Frame(logo_frame, bg=C["topbar_bg"])
        title_frame.pack(side=tk.LEFT, padx=6)
        tk.Label(title_frame, text="Rutas Óptimas · Cusco",
                 bg=C["topbar_bg"], fg=C["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W)
        tk.Label(title_frame, text="UNSAAC · Programación III · 2026",
                 bg=C["topbar_bg"], fg=C["text3"],
                 font=("Segoe UI", 8)).pack(anchor=tk.W)

        # Separador vertical
        tk.Frame(bar, bg=C["panel_border"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=12, padx=8)

        # Chips de algoritmo en la topbar
        chips_frame = tk.Frame(bar, bg=C["topbar_bg"])
        chips_frame.pack(side=tk.LEFT, pady=14)
        for i, (label, _) in enumerate(ALGO_TABS):
            short = label.split(" ")[0] + " " + label.split(" ")[1] if len(label.split(" ")) > 1 else label
            btn = tk.Button(chips_frame, text=short,
                            command=lambda idx=i: self._switch_tab(idx),
                            bg=C["chip_bg"], fg=C["text2"],
                            font=("Segoe UI", 9), relief=tk.FLAT,
                            padx=10, pady=3, cursor="hand2",
                            activebackground=C["tag_blue"],
                            activeforeground=C["accent"],
                            bd=0)
            btn.pack(side=tk.LEFT, padx=2)
            self._tab_buttons.append(btn)

        # Info del mapa (derecha)
        self.lbl_topbar_info = tk.Label(bar, text="",
            bg=C["topbar_bg"], fg=C["text2"],
            font=("Segoe UI", 9))
        self.lbl_topbar_info.pack(side=tk.RIGHT, padx=20)

    # ─── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        # Contenedor de todas las pantallas (apiladas)
        self.tab_container = tk.Frame(self.sidebar, bg=C["panel_bg"])
        self.tab_container.pack(fill=tk.BOTH, expand=True)

        # Instanciar cada tab
        nb = self.tab_container  # "notebook" falso – cada tab gestiona su frame
        self.tab_datos        = DatosTab(nb, self)
        self.tab_ordenacion   = OrdenacionTab(nb, self)
        self.tab_greedy       = GreedyTab(nb, self)
        self.tab_divide       = DivideTab(nb, self)
        self.tab_pd           = PDTab(nb, self)
        self.tab_backtracking = BacktrackingTab(nb, self)

        # Mostrar la primera
        self._switch_tab(0)

    # ─── Mapa ─────────────────────────────────────────────────────────────────
    def _build_mapa(self):
        # Canvas que llena todo el frame del mapa
        self.canvas_mapa = tk.Canvas(self.mapa_frame,
            bg=C["map_bg"], highlightthickness=0, cursor="crosshair")
        self.canvas_mapa.pack(fill=tk.BOTH, expand=True)
        self.canvas_mapa.bind("<Configure>", lambda e: self._dibujar_mapa())
        self._dibujar_mapa()

        # Overlay: leyenda esquina inferior derecha
        self._overlay_leyenda()

    def _overlay_leyenda(self):
        """Leyenda flotante sobre el mapa."""
        ley = tk.Frame(self.mapa_frame, bg=C["panel_bg"],
                       relief=tk.FLAT, bd=0)
        ley.place(relx=1.0, rely=1.0, anchor="se", x=-14, y=-14)

        items = [
            (C["node_fill"],  "Zona del mapa"),
            (C["route_blue"], "Ruta activa"),
            (C["red"],        "Pedido urgente"),
            (C["yellow"],     "#202124", "Pedido normal"),
            (C["accent2"],    "Repartidor"),
        ]
        for item in items:
            if len(item) == 2:
                col, txt = item; txt_col = C["text2"]
            else:
                col, txt_col, txt = item[0], item[1], item[2]
            row = tk.Frame(ley, bg=C["panel_bg"])
            row.pack(fill=tk.X, padx=8, pady=1)
            tk.Canvas(row, width=12, height=12, bg=C["panel_bg"],
                      highlightthickness=0).pack(side=tk.LEFT)
            # dibujar círculo en canvas
            c2 = tk.Canvas(row, width=12, height=12,
                           bg=C["panel_bg"], highlightthickness=0)
            c2.pack(side=tk.LEFT)
            c2.create_oval(1, 1, 11, 11, fill=col, outline="")
            tk.Label(row, text=txt, bg=C["panel_bg"], fg=C["text2"],
                     font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=4)

    # ─── Dibujar mapa ─────────────────────────────────────────────────────────
    def _dibujar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        cv = self.canvas_mapa
        cv.delete("all")
        W = cv.winfo_width()  or 800
        H = cv.winfo_height() or 700
        if W < 50: W = 800
        if H < 50: H = 700

        MX, MY = 48, 44   # márgenes

        def to_px(x, y):
            px = MX + (x / 100) * (W - 2 * MX)
            py = H - MY - (y / 100) * (H - 2 * MY)
            return px, py

        # ── Fondo tipo mapa ──
        # Cuadrícula sutil
        for i in range(0, 101, 5):
            gx, _ = to_px(i, 0); _, gy = to_px(0, i)
            cv.create_line(gx, MY, gx, H - MY, fill="#ddd6cc", width=1 if i % 10 == 0 else 0)
            cv.create_line(MX, gy, W - MX, gy, fill="#ddd6cc", width=1 if i % 10 == 0 else 0)

        # ── Cuadrantes (Divide y Vencerás) ──
        if cuadrantes:
            quad_colors = ["#ddeeff", "#ddf5e8", "#fff9cc", "#fce4ec"]
            quad_borders = ["#90caf9", "#a5d6a7", "#fff176", "#f48fb1"]
            for idx, quad in enumerate(cuadrantes):
                bnd = quad["bounds"]
                x1, y1 = to_px(bnd[0], bnd[3])
                x2, y2 = to_px(bnd[1], bnd[2])
                ci = idx % len(quad_colors)
                cv.create_rectangle(x1, y1, x2, y2,
                    fill=quad_colors[ci], outline=quad_borders[ci],
                    width=2, dash=(6, 3))

        # ── Aristas ──
        grafo = construir_grafo()
        dibujadas = set()
        for na, vecinos in grafo.items():
            for nb, peso in vecinos:
                key = tuple(sorted([na, nb]))
                if key in dibujadas: continue
                dibujadas.add(key)
                en_ruta = False
                if ruta_resaltada and len(ruta_resaltada) > 1:
                    for i in range(len(ruta_resaltada) - 1):
                        if {ruta_resaltada[i], ruta_resaltada[i+1]} == {na, nb}:
                            en_ruta = True; break
                ax, ay = to_px(*NODOS[na])
                bx, by = to_px(*NODOS[nb])
                if en_ruta:
                    # Sombra de ruta
                    cv.create_line(ax, ay, bx, by, fill="#a8c7fa", width=10,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    cv.create_line(ax, ay, bx, by, fill=C["route_blue"], width=5,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                else:
                    cv.create_line(ax, ay, bx, by, fill="#c8bfb2", width=2,
                                   capstyle=tk.ROUND)
                # Tiempo
                mx, my = (ax+bx)/2, (ay+by)/2
                if not en_ruta:
                    cv.create_text(mx, my, text=str(peso)+"m",
                                   fill=C["text3"], font=("Segoe UI", 7))
                else:
                    cv.create_oval(mx-9, my-9, mx+9, my+9,
                                   fill="white", outline=C["route_blue"], width=1)
                    cv.create_text(mx, my, text=str(peso),
                                   fill=C["route_blue"], font=("Segoe UI", 7, "bold"))

        # ── Pedidos ──
        if pedidos_resaltados:
            PRIO_COL = {1: C["red"], 2: C["yellow"], 3: C["accent2"]}
            PRIO_STROKE = {1: "#b71c1c", 2: "#f57f17", 3: "#1b5e20"}
            for p in pedidos_resaltados:
                px, py = to_px(p.coord_x, p.coord_y)
                col = PRIO_COL.get(p.prioridad, C["accent"])
                stroke = PRIO_STROKE.get(p.prioridad, C["accent_dark"])
                # Pin de pedido
                r = 9
                cv.create_oval(px-r, py-r, px+r, py+r,
                               fill=col, outline="white", width=2)
                cv.create_text(px, py, text=str(p.id),
                               fill="white", font=("Segoe UI", 7, "bold"))
                cv.create_text(px, py - r - 8, text=p.cliente.split()[0],
                               fill=stroke, font=("Segoe UI", 7))

        # ── Nodos ──
        for nombre, (nx, ny) in NODOS.items():
            px, py = to_px(nx, ny)
            en_ruta = ruta_resaltada and nombre in ruta_resaltada
            r = 11 if en_ruta else 8
            fill = C["node_sel"] if en_ruta else C["node_fill"]
            stroke = "white"
            sw = 3 if en_ruta else 2
            # Sombra
            cv.create_oval(px-r+2, py-r+2, px+r+2, py+r+2,
                           fill="#bbbbbb", outline="")
            cv.create_oval(px-r, py-r, px+r, py+r,
                           fill=fill, outline=stroke, width=sw)
            if en_ruta:
                cv.create_text(px, py, text="★",
                               fill="white", font=("Segoe UI", 7))

            # Label en fondo blanco redondeado
            lbl_bg = cv.create_rectangle(0, 0, 1, 1,
                fill="white", outline=C["panel_border"], width=1)
            lbl_txt = cv.create_text(px, py - r - 10,
                text=nombre,
                fill=C["text"] if en_ruta else C["text2"],
                font=("Segoe UI", 8, "bold" if en_ruta else "normal"))
            # Ajustar bbox del fondo
            bb = cv.bbox(lbl_txt)
            if bb:
                cv.coords(lbl_bg, bb[0]-3, bb[1]-2, bb[2]+3, bb[3]+2)
                cv.tag_raise(lbl_txt)

        # ── Repartidores ──
        for rep in self.repartidores:
            rx, ry = to_px(rep.pos_x, rep.pos_y)
            size = 11
            cv.create_polygon(
                rx, ry - size,
                rx + size*0.9, ry + size*0.5,
                rx - size*0.9, ry + size*0.5,
                fill=C["accent2"], outline="white", width=2
            )
            cv.create_text(rx, ry + size + 8, text=rep.nombre[:4],
                           fill=C["tag_green_t"],
                           font=("Segoe UI", 7, "bold"))

        # ── Brújula ──
        cx2, cy2 = W - 36, MY + 30
        cv.create_oval(cx2-18, cy2-18, cx2+18, cy2+18,
                       fill="white", outline=C["panel_border"], width=1)
        cv.create_text(cx2, cy2 - 8, text="N", fill=C["red"],
                       font=("Segoe UI", 8, "bold"))
        cv.create_line(cx2, cy2 - 5, cx2, cy2 + 5,
                       fill=C["text3"], width=1)
        cv.create_text(cx2, cy2 + 10, text="S", fill=C["text3"],
                       font=("Segoe UI", 7))

        # ── Escala ──
        sv_x1, sv_y = MX + 10, H - MY - 10
        sv_x2 = sv_x1 + 60
        cv.create_line(sv_x1, sv_y, sv_x2, sv_y, fill=C["text2"], width=2)
        cv.create_line(sv_x1, sv_y - 4, sv_x1, sv_y + 4, fill=C["text2"], width=2)
        cv.create_line(sv_x2, sv_y - 4, sv_x2, sv_y + 4, fill=C["text2"], width=2)
        cv.create_text((sv_x1+sv_x2)//2, sv_y - 10,
                       text="~500 m", fill=C["text2"],
                       font=("Segoe UI", 7))

    # ─── Cambiar tab ──────────────────────────────────────────────────────────
    def _switch_tab(self, idx):
        # Ocultar todos los frames
        for f in self._tab_frames:
            f.pack_forget()
        # Mostrar el seleccionado
        if idx < len(self._tab_frames):
            self._tab_frames[idx].pack(fill=tk.BOTH, expand=True)
        # Actualizar estilos de botones
        for i, btn in enumerate(self._tab_buttons):
            if i == idx:
                btn.config(bg=C["tag_blue"], fg=C["accent"],
                           font=("Segoe UI", 9, "bold"))
            else:
                btn.config(bg=C["chip_bg"], fg=C["text2"],
                           font=("Segoe UI", 9))
        self._tab_index = idx

    def register_tab_frame(self, frame):
        """Llamado por cada Tab al crearse para registrar su frame."""
        self._tab_frames.append(frame)

    # ─── API pública para los tabs ────────────────────────────────────────────
    def actualizar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        self._dibujar_mapa(ruta_resaltada, pedidos_resaltados, cuadrantes)

    def set_info_mapa(self, texto):
        self.lbl_topbar_info.config(text=texto)
