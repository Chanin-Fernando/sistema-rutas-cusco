import tkinter as tk
from tkinter import ttk
from ..data import generar_pedidos, generar_repartidores, construir_grafo, NODOS
from .themes import get_theme
from .theme_utils import retheme_tree
from .tabs import (
    DatosTab,
    OrdenacionTab,
    GreedyTab,
    DivideTab,
    PDTab,
    BacktrackingTab
)

ALGO_TABS = [
    ("📦 Datos",          "datos"),
    ("🔢 Ordenación",     "ordenacion"),
    ("⚡ Greedy",         "greedy"),
    ("🗺 Divide",         "divide"),
    ("💼 P. Dinámica",    "pd"),
    ("🔙 Backtracking",   "backtracking"),
]


class AppCusco(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rutas Óptimas – Cusco")
        self.geometry("1380x800")
        self.minsize(1100, 650)
        self.resizable(True, True)

        self._theme = "light"
        self.COLORES = get_theme(self._theme)
        self.configure(bg=self.COLORES["panel_bg"])

        self.pedidos = generar_pedidos(12)
        self.repartidores = generar_repartidores()

        self._tab_index = 0
        self._tab_frames = []
        self._tab_buttons = []
        self._map_ruta = None
        self._map_pedidos = None
        self._map_cuadrantes = None
        self._leyenda_frame = None

        self._configurar_estilos()
        self._construir_ui()

    # ─── Estilos ttk ──────────────────────────────────────────────────────────
    def _configurar_estilos(self):
        c = self.COLORES
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
            background=c["panel_bg"], foreground=c["text"],
            fieldbackground=c["panel_bg"], rowheight=28,
            font=("Segoe UI", 9), borderwidth=0)
        style.configure("Treeview.Heading",
            background=c["separator"], foreground=c["text2"],
            font=("Segoe UI", 9, "bold"), relief="flat", borderwidth=0)
        style.map("Treeview",
            background=[("selected", c["tag_blue"])],
            foreground=[("selected", c["accent"])])
        style.configure("TCombobox",
            fieldbackground=c["chip_bg"], background=c["chip_bg"],
            foreground=c["text"], selectbackground=c["tag_blue"],
            relief="flat", borderwidth=1)
        style.map("TCombobox", fieldbackground=[("readonly", c["chip_bg"])])
        style.configure("TScrollbar",
            background=c["chip_bg"], troughcolor=c["separator"],
            relief="flat", borderwidth=0, arrowsize=12)

    # ─── Layout principal ─────────────────────────────────────────────────────
    def _construir_ui(self):
        # ── Barra superior tipo Google Maps ──
        self._build_topbar()

        # ── Cuerpo: sidebar izquierdo + mapa derecho ──
        c = self.COLORES
        self._body_frame = tk.Frame(self, bg=c["separator"])
        self._body_frame.pack(fill=tk.BOTH, expand=True)
        body = self._body_frame

        # Mapa primero (ocupa el resto) — debe existir antes de que los tabs llamen actualizar_mapa
        self.mapa_frame = tk.Frame(body, bg=c["map_bg"])
        self.mapa_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_mapa()

        # Separador
        self._sidebar_sep = tk.Frame(body, bg=c["panel_border"], width=1)
        self._sidebar_sep.pack(side=tk.RIGHT, fill=tk.Y)

        # Sidebar (se construye después, cuando canvas_mapa ya existe)
        self.sidebar = tk.Frame(body, bg=c["panel_bg"], width=380)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

    # ─── Barra superior ───────────────────────────────────────────────────────
    def _build_topbar(self):
        c = self.COLORES
        self.topbar = tk.Frame(self, bg=c["topbar_bg"], height=56)
        self.topbar.pack(fill=tk.X)
        self.topbar.pack_propagate(False)
        bar = self.topbar

        # Botón menú (estilo Google Maps)
        self.btn_menu = tk.Button(
            bar, text="☰", command=self._show_menu,
            bg=c["chip_bg"], fg=c["text"],
            font=("Segoe UI", 14), relief=tk.FLAT,
            padx=10, pady=2, cursor="hand2", bd=0,
            activebackground=c["tag_blue"],
            activeforeground=c["accent"],
        )
        self.btn_menu.pack(side=tk.LEFT, padx=(14, 6), pady=10)

        # Logo / título
        logo_frame = tk.Frame(bar, bg=c["topbar_bg"])
        logo_frame.pack(side=tk.LEFT, padx=(4, 12), pady=8)
        tk.Label(logo_frame, text="🗺", bg=c["topbar_bg"],
                 font=("Segoe UI", 20)).pack(side=tk.LEFT)
        title_frame = tk.Frame(logo_frame, bg=c["topbar_bg"])
        title_frame.pack(side=tk.LEFT, padx=6)
        tk.Label(title_frame, text="Rutas Óptimas · Cusco",
                 bg=c["topbar_bg"], fg=c["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W)
        tk.Label(title_frame, text="UNSAAC · Programación III · 2026",
                 bg=c["topbar_bg"], fg=c["text3"],
                 font=("Segoe UI", 8)).pack(anchor=tk.W)

        # Separador vertical
        tk.Frame(bar, bg=c["panel_border"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=12, padx=8)

        # Chips de algoritmo en la topbar
        chips_frame = tk.Frame(bar, bg=c["topbar_bg"])
        chips_frame.pack(side=tk.LEFT, pady=14)
        for i, (label, _) in enumerate(ALGO_TABS):
            short = label.split(" ")[0] + " " + label.split(" ")[1] if len(label.split(" ")) > 1 else label
            btn = tk.Button(chips_frame, text=short,
                            command=lambda idx=i: self._switch_tab(idx),
                            bg=c["chip_bg"], fg=c["text2"],
                            font=("Segoe UI", 9), relief=tk.FLAT,
                            padx=10, pady=3, cursor="hand2",
                            activebackground=c["tag_blue"],
                            activeforeground=c["accent"],
                            bd=0)
            btn.pack(side=tk.LEFT, padx=2)
            self._tab_buttons.append(btn)

        # Info del mapa (derecha)
        self.lbl_topbar_info = tk.Label(bar, text="",
            bg=c["topbar_bg"], fg=c["text2"],
            font=("Segoe UI", 9))
        self.lbl_topbar_info.pack(side=tk.RIGHT, padx=(8, 16))

    # ─── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        # Contenedor de todas las pantallas (apiladas)
        self.tab_container = tk.Frame(self.sidebar, bg=self.COLORES["panel_bg"])
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
            bg=self.COLORES["map_bg"], highlightthickness=0, cursor="crosshair")
        self.canvas_mapa.pack(fill=tk.BOTH, expand=True)
        self.canvas_mapa.bind("<Configure>", lambda e: self._dibujar_mapa())
        self._dibujar_mapa()

        # Overlay: leyenda esquina inferior derecha
        self._overlay_leyenda()

    def _overlay_leyenda(self):
        """Leyenda flotante sobre el mapa."""
        if self._leyenda_frame is not None:
            self._leyenda_frame.destroy()
        c = self.COLORES
        ley = tk.Frame(self.mapa_frame, bg=c["panel_bg"], relief=tk.FLAT, bd=0)
        ley.place(relx=1.0, rely=1.0, anchor="se", x=-14, y=-14)
        self._leyenda_frame = ley

        items = [
            (c["node_fill"],  "Zona del mapa"),
            (c["route_blue"], "Ruta activa"),
            (c["red"],        "Pedido urgente"),
            (c["yellow"],     "Pedido normal"),
            (c["accent2"],    "Repartidor"),
        ]
        for col, txt in items:
            row = tk.Frame(ley, bg=c["panel_bg"])
            row.pack(fill=tk.X, padx=8, pady=1)
            c2 = tk.Canvas(row, width=12, height=12,
                           bg=c["panel_bg"], highlightthickness=0)
            c2.pack(side=tk.LEFT)
            c2.create_oval(1, 1, 11, 11, fill=col, outline="")
            tk.Label(row, text=txt, bg=c["panel_bg"], fg=c["text2"],
                     font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=4)

    # ─── Dibujar mapa ─────────────────────────────────────────────────────────
    def _dibujar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        c = self.COLORES
        cv = self.canvas_mapa
        cv.config(bg=c["map_bg"])
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
            grid_col = c["map_grid_major"] if i % 10 == 0 else c["map_grid"]
            w_line = 1 if i % 10 == 0 else 0
            cv.create_line(gx, MY, gx, H - MY, fill=grid_col, width=w_line)
            cv.create_line(MX, gy, W - MX, gy, fill=grid_col, width=w_line)

        # ── Cuadrantes (Divide y Vencerás) ──
        if cuadrantes:
            quad_colors = c["quad_fills"]
            quad_borders = c["quad_borders"]
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
                    cv.create_line(ax, ay, bx, by, fill=c["map_route_glow"], width=10,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    cv.create_line(ax, ay, bx, by, fill=c["route_blue"], width=5,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                else:
                    cv.create_line(ax, ay, bx, by, fill=c["map_edge"], width=2,
                                   capstyle=tk.ROUND)
                mx, my = (ax+bx)/2, (ay+by)/2
                if not en_ruta:
                    cv.create_text(mx, my, text=str(peso)+"m",
                                   fill=c["text3"], font=("Segoe UI", 7))
                else:
                    cv.create_oval(mx-9, my-9, mx+9, my+9,
                                   fill=c["map_label_bg"], outline=c["route_blue"], width=1)
                    cv.create_text(mx, my, text=str(peso),
                                   fill=c["route_blue"], font=("Segoe UI", 7, "bold"))

        # ── Pedidos ──
        if pedidos_resaltados:
            PRIO_COL = {1: c["red"], 2: c["yellow"], 3: c["accent2"]}
            PRIO_STROKE = {1: c["tag_red_t"], 2: c["warning"], 3: c["tag_green_t"]}
            for p in pedidos_resaltados:
                px, py = to_px(p.coord_x, p.coord_y)
                col = PRIO_COL.get(p.prioridad, c["accent"])
                stroke = PRIO_STROKE.get(p.prioridad, c["accent_dark"])
                r = 9
                cv.create_oval(px-r, py-r, px+r, py+r,
                               fill=col, outline=c["map_label_bg"], width=2)
                cv.create_text(px, py, text=str(p.id),
                               fill=c["map_label_bg"], font=("Segoe UI", 7, "bold"))
                cv.create_text(px, py - r - 8, text=p.cliente.split()[0],
                               fill=stroke, font=("Segoe UI", 7))

        # ── Nodos ──
        for nombre, (nx, ny) in NODOS.items():
            px, py = to_px(nx, ny)
            en_ruta = ruta_resaltada and nombre in ruta_resaltada
            r = 11 if en_ruta else 8
            fill = c["node_sel"] if en_ruta else c["node_fill"]
            stroke = c["map_label_bg"]
            sw = 3 if en_ruta else 2
            cv.create_oval(px-r+2, py-r+2, px+r+2, py+r+2,
                           fill=c["map_shadow"], outline="")
            cv.create_oval(px-r, py-r, px+r, py+r,
                           fill=fill, outline=stroke, width=sw)
            if en_ruta:
                cv.create_text(px, py, text="★",
                               fill=c["map_label_bg"], font=("Segoe UI", 7))

            lbl_bg = cv.create_rectangle(0, 0, 1, 1,
                fill=c["map_label_bg"], outline=c["panel_border"], width=1)
            lbl_txt = cv.create_text(px, py - r - 10,
                text=nombre,
                fill=c["text"] if en_ruta else c["text2"],
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
                fill=c["accent2"], outline=c["map_label_bg"], width=2
            )
            cv.create_text(rx, ry + size + 8, text=rep.nombre[:4],
                           fill=c["tag_green_t"],
                           font=("Segoe UI", 7, "bold"))

        cx2, cy2 = W - 36, MY + 30
        cv.create_oval(cx2-18, cy2-18, cx2+18, cy2+18,
                       fill=c["map_label_bg"], outline=c["panel_border"], width=1)
        cv.create_text(cx2, cy2 - 8, text="N", fill=c["red"],
                       font=("Segoe UI", 8, "bold"))
        cv.create_line(cx2, cy2 - 5, cx2, cy2 + 5,
                       fill=c["text3"], width=1)
        cv.create_text(cx2, cy2 + 10, text="S", fill=c["text3"],
                       font=("Segoe UI", 7))

        sv_x1, sv_y = MX + 10, H - MY - 10
        sv_x2 = sv_x1 + 60
        cv.create_line(sv_x1, sv_y, sv_x2, sv_y, fill=c["text2"], width=2)
        cv.create_line(sv_x1, sv_y - 4, sv_x1, sv_y + 4, fill=c["text2"], width=2)
        cv.create_line(sv_x2, sv_y - 4, sv_x2, sv_y + 4, fill=c["text2"], width=2)
        cv.create_text((sv_x1+sv_x2)//2, sv_y - 10,
                       text="~500 m", fill=c["text2"],
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
        c = self.COLORES
        for i, btn in enumerate(self._tab_buttons):
            if i == idx:
                btn.config(bg=c["tag_blue"], fg=c["accent"],
                           font=("Segoe UI", 9, "bold"))
            else:
                btn.config(bg=c["chip_bg"], fg=c["text2"],
                           font=("Segoe UI", 9))
        self._tab_index = idx

    def register_tab_frame(self, frame):
        """Llamado por cada Tab al crearse para registrar su frame."""
        self._tab_frames.append(frame)

    # ─── Menú y tema ──────────────────────────────────────────────────────────
    def _show_menu(self):
        c = self.COLORES
        menu = tk.Menu(
            self, tearoff=0,
            bg=c["menu_bg"], fg=c["menu_fg"],
            activebackground=c["menu_active_bg"],
            activeforeground=c["menu_active_fg"],
            relief=tk.FLAT, borderwidth=1,
            font=("Segoe UI", 10),
        )
        if self._theme == "light":
            menu.add_command(
                label="  🌙  Tema oscuro",
                command=self._toggle_theme,
            )
        else:
            menu.add_command(
                label="  ☀️  Tema claro",
                command=self._toggle_theme,
            )
        x = self.btn_menu.winfo_rootx()
        y = self.btn_menu.winfo_rooty() + self.btn_menu.winfo_height()
        menu.tk_popup(x, y)

    def _toggle_theme(self):
        old_palette = dict(self.COLORES)
        self._theme = "dark" if self._theme == "light" else "light"
        new_palette = get_theme(self._theme)
        self.COLORES.clear()
        self.COLORES.update(new_palette)

        self.configure(bg=self.COLORES["panel_bg"])
        self._configurar_estilos()
        retheme_tree(self, old_palette, self.COLORES)

        self._body_frame.config(bg=self.COLORES["separator"])
        self._sidebar_sep.config(bg=self.COLORES["panel_border"])
        self.mapa_frame.config(bg=self.COLORES["map_bg"])
        self.sidebar.config(bg=self.COLORES["panel_bg"])
        self.tab_container.config(bg=self.COLORES["panel_bg"])

        self._overlay_leyenda()
        self._switch_tab(self._tab_index)
        self._dibujar_mapa(
            self._map_ruta, self._map_pedidos, self._map_cuadrantes
        )
        tema_txt = "oscuro" if self._theme == "dark" else "claro"
        self.set_info_mapa(f"Tema {tema_txt} activado")

    # ─── API pública para los tabs ────────────────────────────────────────────
    def actualizar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        self._map_ruta = ruta_resaltada
        self._map_pedidos = pedidos_resaltados
        self._map_cuadrantes = cuadrantes
        self._dibujar_mapa(ruta_resaltada, pedidos_resaltados, cuadrantes)

    def set_info_mapa(self, texto):
        self.lbl_topbar_info.config(text=texto)
