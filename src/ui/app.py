import tkinter as tk
from tkinter import ttk, font as tkfont, filedialog, messagebox
import math
import time
import os

# Pillow para imagen de fondo (pip install pillow)
try:
    from PIL import Image, ImageTk, ImageEnhance
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

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
from .themes import get_theme, THEME_LIGHT, THEME_DARK
from .theme_utils import retheme_tree, apply_text_tags

# ─── Paleta Google Maps Light ─────────────────────────────────────────────────
C = {
    "map_bg":       "#e8e0d8",
    "map_road":     "#ffffff",
    "map_road2":    "#f5e9c6",
    "map_water":    "#a8d4f0",
    "map_park":     "#c8e6c9",
    "panel_bg":     "#ffffff",
    "panel_border": "#e0e0e0",
    "topbar_bg":    "#ffffff",
    "accent":       "#1a73e8",
    "accent_dark":  "#1557b0",
    "accent2":      "#34a853",
    "red":          "#ea4335",
    "yellow":       "#fbbc04",
    "text":         "#202124",
    "text2":        "#5f6368",
    "text3":        "#80868b",
    "chip_bg":      "#f1f3f4",
    "chip_hover":   "#e8eaed",
    "route_blue":   "#4285f4",
    "route_stroke": "#1a56d6",
    "node_fill":    "#4285f4",
    "node_sel":     "#ea4335",
    "node_origen":  "#34a853",   # verde = nodo origen seleccionado
    "node_destino": "#ea4335",   # rojo  = nodo destino seleccionado
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
    COLORES = C

    def __init__(self):
        super().__init__()
        self.title("Rutas Óptimas – Cusco")
        self.geometry("1380x800")
        self.minsize(1100, 650)
        self.configure(bg=C["panel_bg"])
        self.resizable(True, True)

        self.pedidos      = generar_pedidos(12)
        self.repartidores = generar_repartidores()

        # ── Tema activo ──────────────────────────────────────────────────────
        self._tema_actual  = "light"   # "light" | "dark"
        self._palette_prev = dict(C)   # copia para retheme diff

        self._tab_index   = 0
        self._tab_frames  = []
        self._tab_buttons = []

        # ── Estado imagen de fondo ──────────────────────────────────────────
        self._bg_image_pil  = None   # objeto PIL original
        self._bg_image_tk   = None   # PhotoImage cacheado
        self._bg_cache_size = (0, 0) # (W, H) de la última vez que se escaló
        self._bg_opacidad   = 0.55   # 0.0 = invisible, 1.0 = opaco

        # ── Estado zoom / pan ───────────────────────────────────────────────
        self._zoom         = 1.0     # escala actual
        self._pan_x        = 0.0     # desplazamiento en unidades del canvas (0-100)
        self._pan_y        = 0.0
        self._drag_start   = None    # (x_pixel, y_pixel) inicio de arrastre

        # ── Estado selección de nodos por clic ─────────────────────────────
        self._nodo_origen  = None
        self._nodo_destino = None
        self._modo_seleccion = False  # True = esperando clic del usuario

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
        self._build_topbar()

        body = tk.Frame(self, bg=C["separator"])
        body.pack(fill=tk.BOTH, expand=True)

        self.mapa_frame = tk.Frame(body, bg=C["map_bg"])
        self.mapa_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_mapa()

        tk.Frame(body, bg=C["panel_border"], width=1).pack(side=tk.RIGHT, fill=tk.Y)

        self.sidebar = tk.Frame(body, bg=C["panel_bg"], width=380)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

    # ─── Barra superior ───────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["topbar_bg"], height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        self._topbar = bar  # guardar referencia para retheme

        # ── Menú hamburguesa (⋮) ─────────────────────────────────────────────
        self._menu_btn = tk.Button(
            bar, text="⋮",
            bg=C["topbar_bg"], fg=C["text2"],
            font=("Segoe UI", 18), relief=tk.FLAT,
            padx=10, pady=0, cursor="hand2", bd=0,
            activebackground=C["chip_bg"],
            activeforeground=C["text"],
            command=self._mostrar_menu)
        self._menu_btn.pack(side=tk.LEFT, padx=(8, 0), pady=6)

        # ── Logo / título ─────────────────────────────────────────────────────
        logo_frame = tk.Frame(bar, bg=C["topbar_bg"])
        logo_frame.pack(side=tk.LEFT, padx=(4, 20), pady=8)
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

        tk.Frame(bar, bg=C["panel_border"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=12, padx=8)

        # ── Chips de algoritmos ───────────────────────────────────────────────
        chips_frame = tk.Frame(bar, bg=C["topbar_bg"])
        chips_frame.pack(side=tk.LEFT, pady=14)
        for i, (label, _) in enumerate(ALGO_TABS):
            parts = label.split(" ")
            short = parts[0] + " " + parts[1] if len(parts) > 1 else label
            btn = tk.Button(chips_frame, text=short,
                            command=lambda idx=i: self._switch_tab(idx),
                            bg=C["chip_bg"], fg=C["text2"],
                            font=("Segoe UI", 9), relief=tk.FLAT,
                            padx=10, pady=3, cursor="hand2",
                            activebackground=C["tag_blue"],
                            activeforeground=C["accent"], bd=0)
            btn.pack(side=tk.LEFT, padx=2)
            self._tab_buttons.append(btn)

        # ── Herramientas del mapa (derecha) ───────────────────────────────────
        tools_frame = tk.Frame(bar, bg=C["topbar_bg"])
        tools_frame.pack(side=tk.RIGHT, padx=10)

        self.btn_mapa_img = tk.Button(
            tools_frame, text="🖼 Mapa",
            command=self._cargar_imagen_fondo,
            bg=C["chip_bg"], fg=C["text2"],
            font=("Segoe UI", 9), relief=tk.FLAT,
            padx=8, pady=3, cursor="hand2", bd=0)
        self.btn_mapa_img.pack(side=tk.LEFT, padx=2)

        tk.Button(tools_frame, text="✕ Fondo",
                  command=self._quitar_imagen_fondo,
                  bg=C["chip_bg"], fg=C["text2"],
                  font=("Segoe UI", 9), relief=tk.FLAT,
                  padx=8, pady=3, cursor="hand2", bd=0
                  ).pack(side=tk.LEFT, padx=2)

        tk.Label(tools_frame, text="Opacidad:", bg=C["topbar_bg"],
                 fg=C["text3"], font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(8, 2))
        self.slider_opacidad = tk.Scale(
            tools_frame, from_=10, to=100, orient=tk.HORIZONTAL,
            length=80, showvalue=False, bg=C["topbar_bg"],
            highlightthickness=0, troughcolor=C["chip_bg"],
            command=self._cambiar_opacidad)
        self.slider_opacidad.set(int(self._bg_opacidad * 100))
        self.slider_opacidad.pack(side=tk.LEFT)

        tk.Button(tools_frame, text="⊙ Reset",
                  command=self._reset_zoom,
                  bg=C["chip_bg"], fg=C["text2"],
                  font=("Segoe UI", 9), relief=tk.FLAT,
                  padx=8, pady=3, cursor="hand2", bd=0
                  ).pack(side=tk.LEFT, padx=2)

        self.lbl_topbar_info = tk.Label(bar, text="",
            bg=C["topbar_bg"], fg=C["text2"], font=("Segoe UI", 9))
        self.lbl_topbar_info.pack(side=tk.RIGHT, padx=10)

    # ─── Menú desplegable ─────────────────────────────────────────────────────
    def _mostrar_menu(self):
        """Crea y muestra el menú flotante debajo del botón ⋮."""
        C_now = self.COLORES

        # Destruir menú anterior si existe
        if hasattr(self, "_menu_popup") and self._menu_popup.winfo_exists():
            self._menu_popup.destroy()
            return

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)      # sin decoración de ventana
        popup.attributes("-topmost", True)
        popup.configure(bg=C_now["panel_border"])
        self._menu_popup = popup

        # Posicionar justo debajo del botón ⋮
        bx = self._menu_btn.winfo_rootx()
        by = self._menu_btn.winfo_rooty() + self._menu_btn.winfo_height()
        popup.geometry(f"220x130+{bx}+{by}")

        inner = tk.Frame(popup, bg=C_now["panel_bg"],
                         relief=tk.FLAT, bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # ── Etiqueta del tema actual ──
        tema_label = "🌙  Cambiar a Modo Oscuro" if self._tema_actual == "light" \
                     else "☀  Cambiar a Modo Claro"

        def _item(parent, icon_text, command):
            f = tk.Frame(parent, bg=C_now["panel_bg"], cursor="hand2")
            f.pack(fill=tk.X)
            lbl = tk.Label(f, text=icon_text,
                           bg=C_now["panel_bg"], fg=C_now["text"],
                           font=("Segoe UI", 10), anchor=tk.W,
                           padx=16, pady=9)
            lbl.pack(fill=tk.X)
            def on_enter(e):
                f.config(bg=C_now["chip_bg"])
                lbl.config(bg=C_now["chip_bg"])
            def on_leave(e):
                f.config(bg=C_now["panel_bg"])
                lbl.config(bg=C_now["panel_bg"])
            def on_click(e):
                popup.destroy()
                command()
            f.bind("<Enter>", on_enter)
            f.bind("<Leave>", on_leave)
            f.bind("<Button-1>", on_click)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", on_click)
            return f

        _item(inner, tema_label, self._toggle_tema)
        tk.Frame(inner, bg=C_now["panel_border"], height=1).pack(fill=tk.X, padx=12)
        _item(inner, "📖  Documentación (GitHub)", self._abrir_documentacion)
        tk.Frame(inner, bg=C_now["panel_border"], height=1).pack(fill=tk.X, padx=12)
        _item(inner, "ℹ  Acerca del proyecto", self._mostrar_acerca)

        # Cerrar al clic fuera del menú
        popup.bind("<FocusOut>", lambda e: popup.destroy() if popup.winfo_exists() else None)
        popup.focus_set()

    # ─── Acciones del menú ────────────────────────────────────────────────────
    def _toggle_tema(self):
        """Alterna entre tema claro y oscuro y re-aplica a todos los widgets."""
        import tkinter.ttk as ttk

        nuevo = "dark" if self._tema_actual == "light" else "light"
        nueva_paleta = get_theme(nuevo)
        vieja_paleta = get_theme(self._tema_actual)

        # Actualizar la paleta global C
        C.update(nueva_paleta)
        self.COLORES = C

        self._tema_actual = nuevo

        # Re-aplicar colores a toda la jerarquía de widgets
        retheme_tree(self, vieja_paleta, nueva_paleta)

        # Actualizar estilos ttk (Treeview, Combobox, Scrollbar)
        style = ttk.Style(self)
        style.configure("Treeview",
            background=C["panel_bg"], foreground=C["text"],
            fieldbackground=C["panel_bg"])
        style.configure("Treeview.Heading",
            background=C["separator"], foreground=C["text2"])
        style.map("Treeview",
            background=[("selected", C["tag_blue"])],
            foreground=[("selected", C["accent"])])
        style.configure("TCombobox",
            fieldbackground=C["chip_bg"], background=C["chip_bg"],
            foreground=C["text"], selectbackground=C["tag_blue"])
        style.map("TCombobox", fieldbackground=[("readonly", C["chip_bg"])])
        style.configure("TScrollbar",
            background=C["chip_bg"], troughcolor=C["separator"])

        # Forzar color de fondo de la raíz y frames principales
        self.configure(bg=C["panel_bg"])
        if hasattr(self, "sidebar"):
            self.sidebar.configure(bg=C["panel_bg"])
        if hasattr(self, "mapa_frame"):
            self.mapa_frame.configure(bg=C["map_bg"])
            self.canvas_mapa.configure(bg=C["map_bg"])

        # Redibujar mapa con los nuevos colores
        self._dibujar_mapa()

    def _abrir_documentacion(self):
        """Abre la página de documentación en el navegador."""
        import webbrowser
        webbrowser.open("https://github.com/Chanin-Fernando/sistema-rutas-cusco#")

    def _mostrar_acerca(self):
        """Muestra un diálogo con información del proyecto."""
        C_now = self.COLORES

        win = tk.Toplevel(self)
        win.title("Acerca del proyecto")
        win.geometry("380x260")
        win.resizable(False, False)
        win.configure(bg=C_now["panel_bg"])
        win.grab_set()

        # Encabezado
        header = tk.Frame(win, bg=C_now["accent"], height=6)
        header.pack(fill=tk.X)

        tk.Label(win, text="🗺  Rutas Óptimas · Cusco",
                 bg=C_now["panel_bg"], fg=C_now["text"],
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 2))
        tk.Label(win, text="Sistema de Gestión de Rutas Óptimas",
                 bg=C_now["panel_bg"], fg=C_now["text2"],
                 font=("Segoe UI", 9)).pack()

        tk.Frame(win, bg=C_now["separator"], height=1).pack(fill=tk.X, padx=24, pady=12)

        info = [
            ("Universidad", "UNSAAC – Programación III"),
            ("Algoritmos",  "Greedy · D&V · PD · Backtracking · QuickSort"),
            ("Entrega",     "Jueves 28 de mayo del 2026"),
            ("Docentes",    "M.Sc. Ugarte R. & M.Sc. Chullo Llave"),
        ]
        for lbl, val in info:
            row = tk.Frame(win, bg=C_now["panel_bg"])
            row.pack(fill=tk.X, padx=28, pady=2)
            tk.Label(row, text=f"{lbl}:", bg=C_now["panel_bg"],
                     fg=C_now["text3"], font=("Segoe UI", 8),
                     width=12, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=val, bg=C_now["panel_bg"],
                     fg=C_now["text"], font=("Segoe UI", 8),
                     anchor=tk.W).pack(side=tk.LEFT)

        tk.Frame(win, bg=C_now["separator"], height=1).pack(fill=tk.X, padx=24, pady=12)

        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg=C_now["accent"], fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=20, pady=6,
                  cursor="hand2", bd=0,
                  activebackground=C_now["accent_dark"],
                  activeforeground="white").pack(pady=(0, 16))

    # ─── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.tab_container = tk.Frame(self.sidebar, bg=C["panel_bg"])
        self.tab_container.pack(fill=tk.BOTH, expand=True)

        nb = self.tab_container
        self.tab_datos        = DatosTab(nb, self)
        self.tab_ordenacion   = OrdenacionTab(nb, self)
        self.tab_greedy       = GreedyTab(nb, self)
        self.tab_divide       = DivideTab(nb, self)
        self.tab_pd           = PDTab(nb, self)
        self.tab_backtracking = BacktrackingTab(nb, self)

        self._switch_tab(0)

    # ─── Mapa ─────────────────────────────────────────────────────────────────
    def _build_mapa(self):
        self.canvas_mapa = tk.Canvas(self.mapa_frame,
            bg=C["map_bg"], highlightthickness=0, cursor="crosshair")
        self.canvas_mapa.pack(fill=tk.BOTH, expand=True)

        # Redibuja cuando cambia tamaño
        self.canvas_mapa.bind("<Configure>",    lambda e: self._on_canvas_resize(e))
        # Zoom con scroll del mouse
        self.canvas_mapa.bind("<MouseWheel>",   self._on_scroll_zoom)        # Windows / macOS
        self.canvas_mapa.bind("<Button-4>",     self._on_scroll_zoom)        # Linux scroll up
        self.canvas_mapa.bind("<Button-5>",     self._on_scroll_zoom)        # Linux scroll down
        # Pan con arrastre (botón central o derecho)
        self.canvas_mapa.bind("<ButtonPress-2>",   self._on_pan_start)
        self.canvas_mapa.bind("<B2-Motion>",       self._on_pan_move)
        self.canvas_mapa.bind("<ButtonRelease-2>", self._on_pan_end)
        # Clic izquierdo → seleccionar nodo
        self.canvas_mapa.bind("<Button-1>", self._on_canvas_clic)
        # Tooltip al mover
        self.canvas_mapa.bind("<Motion>", self._on_mouse_move)

        self._dibujar_mapa()
        self._overlay_leyenda()
        self._overlay_seleccion()

    # ── Imagen de fondo ───────────────────────────────────────────────────────

    def _cargar_imagen_fondo(self):
        """Abre un diálogo para elegir imagen PNG/JPG como fondo del mapa."""
        if not PIL_DISPONIBLE:
            messagebox.showwarning(
                "Pillow no instalado",
                "Instala Pillow para usar imagen de fondo:\n\npip install pillow")
            return
        path = filedialog.askopenfilename(
            title="Seleccionar mapa de Cusco",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")])
        if path:
            self._bg_image_pil  = Image.open(path).convert("RGBA")
            self._bg_cache_size = (0, 0)   # forzar re-escalado
            self._dibujar_mapa()
            self.btn_mapa_img.config(bg=C["tag_blue"], fg=C["accent"])

    def _quitar_imagen_fondo(self):
        self._bg_image_pil  = None
        self._bg_image_tk   = None
        self._bg_cache_size = (0, 0)
        self.btn_mapa_img.config(bg=C["chip_bg"], fg=C["text2"])
        self._dibujar_mapa()

    def _cambiar_opacidad(self, valor):
        self._bg_opacidad   = int(valor) / 100
        self._bg_cache_size = (0, 0)   # forzar re-escalado con nueva opacidad
        self._dibujar_mapa()

    def _preparar_bg(self, W, H):
        """
        Redimensiona y aplica opacidad a la imagen PIL.
        Usa caché: solo recalcula si cambió el tamaño o la opacidad.
        """
        if not PIL_DISPONIBLE or self._bg_image_pil is None:
            return
        if self._bg_cache_size == (W, H, self._bg_opacidad):
            return  # ya está en caché
        img = self._bg_image_pil.copy().resize((W, H), Image.LANCZOS)
        # Aplicar opacidad modificando canal Alpha
        r, g, b, a = img.split()
        a = a.point(lambda p: int(p * self._bg_opacidad))
        img.putalpha(a)
        # Convertir a fondo beige del mapa para preservar color
        fondo = Image.new("RGBA", (W, H), (232, 224, 216, 255))
        fondo.paste(img, mask=img)
        self._bg_image_tk   = ImageTk.PhotoImage(fondo.convert("RGB"))
        self._bg_cache_size = (W, H, self._bg_opacidad)

    # ── Zoom / Pan ────────────────────────────────────────────────────────────

    def _on_canvas_resize(self, event):
        self._bg_cache_size = (0, 0)   # imagen debe re-escalarse
        self._dibujar_mapa()

    def _on_scroll_zoom(self, event):
        # Delta positivo = zoom in, negativo = zoom out
        if hasattr(event, "delta") and event.delta != 0:
            factor = 1.1 if event.delta > 0 else 0.9
        elif event.num == 4:
            factor = 1.1
        else:
            factor = 0.9

        nuevo_zoom = max(0.5, min(5.0, self._zoom * factor))
        if nuevo_zoom == self._zoom:
            return

        # Zoom centrado en el cursor: mantener el punto del mapa bajo el cursor
        W = self.canvas_mapa.winfo_width()  or 800
        H = self.canvas_mapa.winfo_height() or 700
        MX, MY = 48, 44

        # Coordenada del mapa (0-100) bajo el cursor antes del zoom
        mx_map = (event.x - MX) / ((W - 2*MX) * self._zoom / 1.0) * 100 - self._pan_x
        my_map = (H - MY - event.y) / ((H - 2*MY) * self._zoom / 1.0) * 100 - self._pan_y

        self._zoom = nuevo_zoom

        # Ajustar pan para que el punto del mapa quede bajo el cursor
        mx_map2 = (event.x - MX) / ((W - 2*MX) * self._zoom / 1.0) * 100 - self._pan_x
        my_map2 = (H - MY - event.y) / ((H - 2*MY) * self._zoom / 1.0) * 100 - self._pan_y
        self._pan_x += mx_map2 - mx_map
        self._pan_y += my_map2 - my_map

        self._dibujar_mapa()

    def _on_pan_start(self, event):
        self._drag_start = (event.x, event.y)

    def _on_pan_move(self, event):
        if self._drag_start is None:
            return
        W = self.canvas_mapa.winfo_width()  or 800
        H = self.canvas_mapa.winfo_height() or 700
        MX, MY = 48, 44
        dx_px = event.x - self._drag_start[0]
        dy_px = event.y - self._drag_start[1]
        # Convertir píxeles a unidades del mapa
        dx_map = dx_px / ((W - 2*MX) * self._zoom / 100)
        dy_map = -dy_px / ((H - 2*MY) * self._zoom / 100)
        self._pan_x += dx_map
        self._pan_y += dy_map
        self._drag_start = (event.x, event.y)
        self._dibujar_mapa()

    def _on_pan_end(self, event):
        self._drag_start = None

    def _reset_zoom(self):
        self._zoom  = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._dibujar_mapa()

    # ── Selección de nodos por clic ───────────────────────────────────────────

    def _on_canvas_clic(self, event):
        """Detecta si el clic cae sobre algún nodo del mapa."""
        cv = self.canvas_mapa
        W  = cv.winfo_width()  or 800
        H  = cv.winfo_height() or 700

        nodo_cercano = self._nodo_en_pixel(event.x, event.y, W, H, radio=14)
        if nodo_cercano is None:
            return

        if not self._modo_seleccion:
            return

        if self._nodo_origen is None:
            self._nodo_origen = nodo_cercano
            self.lbl_seleccion.config(
                text=f"Origen: {nodo_cercano}  →  clic en destino",
                fg=C["accent2"])
        elif self._nodo_destino is None and nodo_cercano != self._nodo_origen:
            self._nodo_destino = nodo_cercano
            self.lbl_seleccion.config(
                text=f"Origen: {self._nodo_origen}  →  Destino: {nodo_cercano}",
                fg=C["accent"])
            self._modo_seleccion = False
            self.btn_seleccionar.config(text="✎ Seleccionar nodos", bg=C["chip_bg"])
        self._dibujar_mapa()

    def _nodo_en_pixel(self, px, py, W, H, radio=14):
        """Devuelve el nombre del nodo más cercano al pixel (px, py), o None."""
        MX, MY = 48, 44
        zoom   = self._zoom
        pan_x  = self._pan_x
        pan_y  = self._pan_y

        def to_px(x, y):
            nx = MX + ((x + pan_x) / 100) * (W - 2*MX) * zoom
            ny = H - MY - ((y + pan_y) / 100) * (H - 2*MY) * zoom
            return nx, ny

        for nombre, (nx, ny) in NODOS.items():
            npx, npy = to_px(nx, ny)
            if (px - npx)**2 + (py - npy)**2 <= radio**2:
                return nombre
        return None

    def _on_mouse_move(self, event):
        """Muestra tooltip con el nombre del nodo más cercano."""
        cv = self.canvas_mapa
        W  = cv.winfo_width()  or 800
        H  = cv.winfo_height() or 700
        nodo = self._nodo_en_pixel(event.x, event.y, W, H, radio=12)

        cv.delete("tooltip")
        if nodo:
            cv.config(cursor="hand2")
            # Contar conexiones del nodo
            grafo = construir_grafo()
            conexiones = len(grafo.get(nodo, []))
            tip = f"{nodo}  ({conexiones} conexiones)"
            tx, ty = event.x + 14, event.y - 14
            bg = cv.create_rectangle(tx-3, ty-12, tx+len(tip)*6+6, ty+5,
                                     fill="white", outline=C["panel_border"],
                                     width=1, tags="tooltip")
            cv.create_text(tx, ty, text=tip, anchor="w", tags="tooltip",
                           fill=C["text"], font=("Segoe UI", 8))
        else:
            cv.config(cursor="crosshair" if not self._modo_seleccion else "hand2")

    # ── Panel de selección (overlay inferior izquierdo) ───────────────────────

    def _overlay_seleccion(self):
        """Panel flotante para seleccionar nodos con clic."""
        panel = tk.Frame(self.mapa_frame, bg=C["panel_bg"],
                         relief=tk.FLAT, bd=0)
        panel.place(relx=0.0, rely=1.0, anchor="sw", x=14, y=-14)

        self.btn_seleccionar = tk.Button(
            panel, text="✎ Seleccionar nodos",
            command=self._toggle_modo_seleccion,
            bg=C["chip_bg"], fg=C["text2"],
            font=("Segoe UI", 9), relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", bd=0)
        self.btn_seleccionar.pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(panel, text="✕ Limpiar",
                  command=self._limpiar_seleccion,
                  bg=C["chip_bg"], fg=C["text2"],
                  font=("Segoe UI", 9), relief=tk.FLAT,
                  padx=8, pady=4, cursor="hand2", bd=0
                  ).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_seleccion = tk.Label(
            panel, text="Clic en 'Seleccionar nodos' para elegir origen y destino",
            bg=C["panel_bg"], fg=C["text3"], font=("Segoe UI", 8))
        self.lbl_seleccion.pack(side=tk.LEFT)

    def _toggle_modo_seleccion(self):
        self._modo_seleccion = not self._modo_seleccion
        if self._modo_seleccion:
            self._nodo_origen  = None
            self._nodo_destino = None
            self.btn_seleccionar.config(
                text="🔴 Esperando clic...", bg=C["tag_blue"], fg=C["accent"])
            self.lbl_seleccion.config(
                text="Clic en el nodo ORIGEN", fg=C["accent2"])
            self._dibujar_mapa()
        else:
            self.btn_seleccionar.config(
                text="✎ Seleccionar nodos", bg=C["chip_bg"], fg=C["text2"])

    def _limpiar_seleccion(self):
        self._nodo_origen    = None
        self._nodo_destino   = None
        self._modo_seleccion = False
        self.btn_seleccionar.config(
            text="✎ Seleccionar nodos", bg=C["chip_bg"], fg=C["text2"])
        self.lbl_seleccion.config(
            text="Clic en 'Seleccionar nodos' para elegir origen y destino",
            fg=C["text3"])
        self._dibujar_mapa()

    # ── Leyenda ───────────────────────────────────────────────────────────────

    def _overlay_leyenda(self):
        ley = tk.Frame(self.mapa_frame, bg=C["panel_bg"], relief=tk.FLAT, bd=0)
        ley.place(relx=1.0, rely=1.0, anchor="se", x=-14, y=-14)

        items = [
            (C["node_fill"],    "Zona del mapa"),
            (C["node_origen"],  "Origen seleccionado"),
            (C["node_destino"], "Destino seleccionado"),
            (C["route_blue"],   "Ruta activa"),
            (C["red"],          "Pedido urgente"),
            (C["yellow"],       "#202124", "Pedido normal"),
            (C["accent2"],      "Repartidor"),
        ]
        for item in items:
            if len(item) == 2:
                col, txt = item; txt_col = C["text2"]
            else:
                col, txt_col, txt = item[0], item[1], item[2]
            row = tk.Frame(ley, bg=C["panel_bg"])
            row.pack(fill=tk.X, padx=8, pady=1)
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

        MX, MY   = 48, 44
        zoom     = self._zoom
        pan_x    = self._pan_x
        pan_y    = self._pan_y

        def to_px(x, y):
            px = MX + ((x + pan_x) / 100) * (W - 2*MX) * zoom
            py = H - MY - ((y + pan_y) / 100) * (H - 2*MY) * zoom
            return px, py

        # ── Imagen de fondo ──────────────────────────────────────────────────
        if PIL_DISPONIBLE and self._bg_image_pil is not None:
            self._preparar_bg(W, H)
            if self._bg_image_tk:
                cv.create_image(0, 0, anchor="nw", image=self._bg_image_tk)
        else:
            # Cuadrícula sutil cuando no hay imagen
            for i in range(0, 101, 5):
                gx, _ = to_px(i, 0); _, gy = to_px(0, i)
                if MX <= gx <= W - MX:
                    cv.create_line(gx, MY, gx, H - MY,
                                   fill="#ddd6cc",
                                   width=1 if i % 10 == 0 else 0)
                if MY <= gy <= H - MY:
                    cv.create_line(MX, gy, W - MX, gy,
                                   fill="#ddd6cc",
                                   width=1 if i % 10 == 0 else 0)

        # ── Cuadrantes (Divide y Vencerás) ───────────────────────────────────
        if cuadrantes:
            quad_colors  = ["#ddeeff", "#ddf5e8", "#fff9cc", "#fce4ec"]
            quad_borders = ["#90caf9", "#a5d6a7", "#fff176", "#f48fb1"]
            for idx, quad in enumerate(cuadrantes):
                bnd = quad["bounds"]
                x1, y1 = to_px(bnd[0], bnd[3])
                x2, y2 = to_px(bnd[1], bnd[2])
                ci = idx % len(quad_colors)
                cv.create_rectangle(x1, y1, x2, y2,
                    fill=quad_colors[ci], outline=quad_borders[ci],
                    width=2, dash=(6, 3))

        # ── Aristas ───────────────────────────────────────────────────────────
        grafo    = construir_grafo()
        dibujadas = set()
        for na, vecinos in grafo.items():
            for nb, peso in vecinos:
                key = tuple(sorted([na, nb]))
                if key in dibujadas:
                    continue
                dibujadas.add(key)

                en_ruta = False
                if ruta_resaltada and len(ruta_resaltada) > 1:
                    for i in range(len(ruta_resaltada) - 1):
                        if {ruta_resaltada[i], ruta_resaltada[i+1]} == {na, nb}:
                            en_ruta = True; break

                ax, ay = to_px(*NODOS[na])
                bx, by = to_px(*NODOS[nb])

                if en_ruta:
                    cv.create_line(ax, ay, bx, by, fill="#a8c7fa", width=10,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    cv.create_line(ax, ay, bx, by, fill=C["route_blue"], width=5,
                                   capstyle=tk.ROUND, joinstyle=tk.ROUND)
                else:
                    # Si hay imagen de fondo usar línea blanca para mejor contraste
                    color_arista = "#ffffff" if self._bg_image_pil else "#c8bfb2"
                    cv.create_line(ax, ay, bx, by, fill=color_arista, width=2,
                                   capstyle=tk.ROUND)

                mx_l, my_l = (ax+bx)/2, (ay+by)/2
                if not en_ruta:
                    cv.create_text(mx_l, my_l, text=str(peso)+"m",
                                   fill=C["text3"], font=("Segoe UI", 7))
                else:
                    cv.create_oval(mx_l-9, my_l-9, mx_l+9, my_l+9,
                                   fill="white", outline=C["route_blue"], width=1)
                    cv.create_text(mx_l, my_l, text=str(peso),
                                   fill=C["route_blue"], font=("Segoe UI", 7, "bold"))

        # ── Pedidos ───────────────────────────────────────────────────────────
        if pedidos_resaltados:
            PRIO_COL   = {1: C["red"], 2: C["yellow"], 3: C["accent2"]}
            PRIO_STROKE= {1: "#b71c1c", 2: "#f57f17", 3: "#1b5e20"}
            for p in pedidos_resaltados:
                px, py = to_px(p.coord_x, p.coord_y)
                col    = PRIO_COL.get(p.prioridad, C["accent"])
                stroke = PRIO_STROKE.get(p.prioridad, C["accent_dark"])
                r = 9
                cv.create_oval(px-r, py-r, px+r, py+r,
                               fill=col, outline="white", width=2)
                cv.create_text(px, py, text=str(p.id),
                               fill="white", font=("Segoe UI", 7, "bold"))
                cv.create_text(px, py - r - 8, text=p.cliente.split()[0],
                               fill=stroke, font=("Segoe UI", 7))

        # ── Nodos ─────────────────────────────────────────────────────────────
        for nombre, (nx, ny) in NODOS.items():
            px, py = to_px(nx, ny)

            en_ruta  = ruta_resaltada and nombre in ruta_resaltada
            es_orig  = nombre == self._nodo_origen
            es_dest  = nombre == self._nodo_destino

            if es_orig:
                r, fill, sw = 13, C["node_origen"], 3
            elif es_dest:
                r, fill, sw = 13, C["node_destino"], 3
            elif en_ruta:
                r, fill, sw = 11, C["node_sel"], 3
            else:
                r, fill, sw = 8, C["node_fill"], 2

            stroke = "white"
            # Sombra
            cv.create_oval(px-r+2, py-r+2, px+r+2, py+r+2,
                           fill="#bbbbbb", outline="")
            cv.create_oval(px-r, py-r, px+r, py+r,
                           fill=fill, outline=stroke, width=sw)

            if en_ruta:
                cv.create_text(px, py, text="★",
                               fill="white", font=("Segoe UI", 7))
            elif es_orig:
                cv.create_text(px, py, text="A",
                               fill="white", font=("Segoe UI", 8, "bold"))
            elif es_dest:
                cv.create_text(px, py, text="B",
                               fill="white", font=("Segoe UI", 8, "bold"))

            # Label en fondo blanco redondeado
            lbl_bg  = cv.create_rectangle(0, 0, 1, 1,
                fill="white", outline=C["panel_border"], width=1)
            lbl_txt = cv.create_text(px, py - r - 10,
                text=nombre,
                fill=C["text"] if (en_ruta or es_orig or es_dest) else C["text2"],
                font=("Segoe UI", 8,
                      "bold" if (en_ruta or es_orig or es_dest) else "normal"))
            bb = cv.bbox(lbl_txt)
            if bb:
                cv.coords(lbl_bg, bb[0]-3, bb[1]-2, bb[2]+3, bb[3]+2)
                cv.tag_raise(lbl_txt)

        # ── Repartidores ──────────────────────────────────────────────────────
        for rep in self.repartidores:
            rx, ry = to_px(rep.pos_x, rep.pos_y)
            size = 11
            cv.create_polygon(
                rx, ry - size,
                rx + size*0.9, ry + size*0.5,
                rx - size*0.9, ry + size*0.5,
                fill=C["accent2"], outline="white", width=2)
            cv.create_text(rx, ry + size + 8, text=rep.nombre[:4],
                           fill=C["tag_green_t"], font=("Segoe UI", 7, "bold"))

        # ── Brújula ───────────────────────────────────────────────────────────
        cx2, cy2 = W - 36, MY + 30
        cv.create_oval(cx2-18, cy2-18, cx2+18, cy2+18,
                       fill="white", outline=C["panel_border"], width=1)
        cv.create_text(cx2, cy2 - 8,  text="N", fill=C["red"],
                       font=("Segoe UI", 8, "bold"))
        cv.create_line(cx2, cy2 - 5,  cx2, cy2 + 5,
                       fill=C["text3"], width=1)
        cv.create_text(cx2, cy2 + 10, text="S", fill=C["text3"],
                       font=("Segoe UI", 7))

        # Indicador de zoom
        cv.create_text(W - 36, cy2 + 26,
                       text=f"×{self._zoom:.1f}",
                       fill=C["text3"], font=("Segoe UI", 7))

        # ── Escala ────────────────────────────────────────────────────────────
        sv_x1, sv_y = MX + 10, H - MY - 10
        sv_x2 = sv_x1 + 60
        cv.create_line(sv_x1, sv_y, sv_x2, sv_y, fill=C["text2"], width=2)
        cv.create_line(sv_x1, sv_y-4, sv_x1, sv_y+4, fill=C["text2"], width=2)
        cv.create_line(sv_x2, sv_y-4, sv_x2, sv_y+4, fill=C["text2"], width=2)
        cv.create_text((sv_x1+sv_x2)//2, sv_y - 10,
                       text="~500 m", fill=C["text2"], font=("Segoe UI", 7))

    # ─── Cambiar tab ──────────────────────────────────────────────────────────
    def _switch_tab(self, idx):
        for f in self._tab_frames:
            f.pack_forget()
        if idx < len(self._tab_frames):
            self._tab_frames[idx].pack(fill=tk.BOTH, expand=True)
        for i, btn in enumerate(self._tab_buttons):
            if i == idx:
                btn.config(bg=C["tag_blue"], fg=C["accent"],
                           font=("Segoe UI", 9, "bold"))
            else:
                btn.config(bg=C["chip_bg"], fg=C["text2"],
                           font=("Segoe UI", 9))
        self._tab_index = idx

    def register_tab_frame(self, frame):
        self._tab_frames.append(frame)

    # ─── API pública para los tabs ────────────────────────────────────────────
    def actualizar_mapa(self, ruta_resaltada=None, pedidos_resaltados=None, cuadrantes=None):
        self._dibujar_mapa(ruta_resaltada, pedidos_resaltados, cuadrantes)

    def set_info_mapa(self, texto):
        self.lbl_topbar_info.config(text=texto)

    def get_nodo_origen(self):
        """Los tabs pueden leer el nodo origen seleccionado por clic."""
        return self._nodo_origen

    def get_nodo_destino(self):
        """Los tabs pueden leer el nodo destino seleccionado por clic."""
        return self._nodo_destino