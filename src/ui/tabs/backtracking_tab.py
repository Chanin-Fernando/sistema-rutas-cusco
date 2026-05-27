import tkinter as tk
from tkinter import ttk
import time
from ...data import construir_grafo, NODOS
from ...algorithms import Backtracking
from ..base_tab import BaseTab

class BacktrackingTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "🔙 Backtracking",
                      "Todas las rutas posibles · O(V!)")
        nodos_lista = list(NODOS.keys())

        ctrl = self._ctrl_row(self.tab)
        self._label(ctrl, "Origen:").pack(side=tk.LEFT)
        self.var_origen = tk.StringVar(value="San Blas")
        ttk.Combobox(ctrl, textvariable=self.var_origen, values=nodos_lista,
                     width=14, state="readonly",
                     font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

        ctrl2 = self._ctrl_row(self.tab)
        self._label(ctrl2, "Destino:").pack(side=tk.LEFT)
        self.var_destino = tk.StringVar(value="Wanchaq (Túpac Amaru)")
        ttk.Combobox(ctrl2, textvariable=self.var_destino, values=nodos_lista,
                     width=14, state="readonly",
                     font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

        ctrl3 = self._ctrl_row(self.tab)
        self._label(ctrl3, "Calles bloqueadas:").pack(side=tk.LEFT)
        self.var_bloqueadas = tk.StringVar(value="")
        tk.Entry(ctrl3, textvariable=self.var_bloqueadas, width=22,
                 bg=c["chip_bg"], fg=c["text"], font=("Segoe UI", 9),
                 relief=tk.FLAT, highlightthickness=1,
                 highlightbackground=c["panel_border"]).pack(side=tk.LEFT, padx=4)

        self._label(self.tab, "  (ej: San Blas-San Cristóbal, separadas por coma)",
                    small=True).pack(anchor=tk.W, padx=12, pady=(0, 6))

        ctrl4 = self._ctrl_row(self.tab)
        self._boton(ctrl4, "▶ Buscar rutas", self._ejecutar_backtracking).pack(side=tk.LEFT)

        self.txt_bt = self._text_area(self.tab)

    def _ejecutar_backtracking(self):
        origen = self.var_origen.get()
        destino = self.var_destino.get()
        bloq_raw = self.var_bloqueadas.get()
        bloqueadas = [b.strip() for b in bloq_raw.split(",") if b.strip()]
        grafo = construir_grafo(bloqueadas)
        bt = Backtracking(grafo)
        t0 = time.perf_counter()
        mejor_ruta, costo = bt.encontrar_rutas(origen, destino)
        elapsed = (time.perf_counter() - t0) * 1000
        lines = [
            f"── Backtracking: Búsqueda Exhaustiva ──",
            f"{origen}  →  {destino}",
            f"Bloqueadas: {bloqueadas or 'ninguna'}  |  Tiempo: {elapsed:.3f} ms", ""
        ]
        lines.extend(bt.log_pasos)
        self._actualizar_text(self.txt_bt, lines)
        if mejor_ruta:
            self.app.actualizar_mapa(ruta_resaltada=mejor_ruta,
                                     pedidos_resaltados=self.app.pedidos[:3])
            self.app.set_info_mapa(f"Backtracking: mejor ruta {costo} min · {len(mejor_ruta)} zonas")
