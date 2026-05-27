import tkinter as tk
from tkinter import ttk
from ...data import generar_pedidos
from ..base_tab import BaseTab

class DatosTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "📦 Pedidos y Repartidores",
                      "Datos de entrada del sistema")

        # Control de regeneración
        ctrl = self._ctrl_row(self.tab)
        self._label(ctrl, "Cantidad de pedidos:").pack(side=tk.LEFT)
        self.var_n = tk.IntVar(value=12)
        sp = tk.Spinbox(ctrl, from_=4, to=20, textvariable=self.var_n,
                        width=4, bg=c["chip_bg"], fg=c["text"],
                        font=("Segoe UI", 9), relief=tk.FLAT,
                        buttonbackground=c["chip_bg"],
                        highlightthickness=1, highlightbackground=c["panel_border"])
        sp.pack(side=tk.LEFT, padx=6)
        self._chip(ctrl, "⟳ Regenerar", self._regenerar).pack(side=tk.LEFT)

        # Tabla pedidos
        self._label(self.tab, "  Pedidos:").pack(anchor=tk.W, padx=12, pady=(8, 2))
        cols = ("ID", "Cliente", "Sector", "X", "Y", "Prio", "Peso", "S/")
        self.tree_datos = self._tabla(self.tab, cols, height=8)
        self._llenar_datos()

        # Tabla repartidores
        self._separador(self.tab)
        self._label(self.tab, "  Repartidores:").pack(anchor=tk.W, padx=12, pady=(4, 2))
        cols_r = ("ID", "Nombre", "Pos X", "Pos Y", "Cap. kg")
        self.tree_reps = self._tabla(self.tab, cols_r, height=4)
        for r in self.app.repartidores:
            self.tree_reps.insert("", tk.END,
                values=(r.id, r.nombre, r.pos_x, r.pos_y, r.capacidad_max))

        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos)

    def _llenar_datos(self):
        self.tree_datos.delete(*self.tree_datos.get_children())
        PRIO = {1: "🔴 Alta", 2: "🟡 Media", 3: "🟢 Baja"}
        for p in self.app.pedidos:
            self.tree_datos.insert("", tk.END, values=(
                p.id, p.cliente.split()[0], p.sector[:12],
                p.coord_x, p.coord_y,
                PRIO[p.prioridad], p.peso, f"{p.valor:.0f}"
            ))

    def _regenerar(self):
        self.app.pedidos = generar_pedidos(self.var_n.get())
        self._llenar_datos()
        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos)
        self.app.set_info_mapa(f"{len(self.app.pedidos)} pedidos cargados")
