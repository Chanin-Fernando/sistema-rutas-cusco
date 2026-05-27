import tkinter as tk
from tkinter import ttk
import time
from ...algorithms import OrdenacionBusqueda
from ..base_tab import BaseTab

class OrdenacionTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "🔢 Ordenación y Búsqueda",
                      "QuickSort O(n log n) · Búsqueda Binaria O(log n)")

        # QuickSort
        ctrl = self._ctrl_row(self.tab)
        self._label(ctrl, "Ordenar por:").pack(side=tk.LEFT)
        self.var_criterio = tk.StringVar(value="prioridad")
        cb = ttk.Combobox(ctrl, textvariable=self.var_criterio, width=16,
                          values=["prioridad", "valor", "peso", "distancia_origen"],
                          state="readonly", font=("Segoe UI", 9))
        cb.pack(side=tk.LEFT, padx=6)
        self._boton(ctrl, "▶ QuickSort", self._ejecutar_ordenacion).pack(side=tk.LEFT)

        cols = ("ID", "Cliente", "Sector", "Prio", "Peso", "S/")
        self.tree_ord = self._tabla(self.tab, cols, height=7)

        self._separador(self.tab)
        self._label(self.tab, "  Búsqueda Binaria (por ID):").pack(anchor=tk.W, padx=12, pady=(4,2))

        ctrl2 = self._ctrl_row(self.tab)
        self._label(ctrl2, "ID:").pack(side=tk.LEFT)
        self.var_busq_id = tk.IntVar(value=1)
        tk.Spinbox(ctrl2, from_=1, to=50, textvariable=self.var_busq_id,
                   width=5, bg=c["chip_bg"], fg=c["text"],
                   font=("Segoe UI", 9), relief=tk.FLAT,
                   buttonbackground=c["chip_bg"]).pack(side=tk.LEFT, padx=4)
        self._chip(ctrl2, "🔍 Buscar ID", self._buscar_id).pack(side=tk.LEFT, padx=4)

        self._label(self.tab, "  Búsqueda por sector:").pack(anchor=tk.W, padx=12, pady=(8,2))
        ctrl3 = self._ctrl_row(self.tab)
        self.var_busq_sec = tk.StringVar(value="Wanchaq")
        tk.Entry(ctrl3, textvariable=self.var_busq_sec, width=18,
                 bg=c["chip_bg"], fg=c["text"], font=("Segoe UI", 9),
                 relief=tk.FLAT, highlightthickness=1,
                 highlightbackground=c["panel_border"]).pack(side=tk.LEFT)
        self._chip(ctrl3, "🔍 Buscar sector", self._buscar_sector).pack(side=tk.LEFT, padx=6)

        self.res_frame, self.lbl_busq = self._resultado_label(self.tab)
        self.res_frame.pack(fill=tk.X, padx=12, pady=4)
        self.res_frame.pack_forget()

    def _ejecutar_ordenacion(self):
        ob = OrdenacionBusqueda()
        t0 = time.perf_counter()
        ordenados = ob.quicksort_pedidos(self.app.pedidos, self.var_criterio.get())
        elapsed = (time.perf_counter() - t0) * 1000
        PRIO = {1: "🔴 Alta", 2: "🟡 Med", 3: "🟢 Baja"}
        self.tree_ord.delete(*self.tree_ord.get_children())
        for p in ordenados:
            self.tree_ord.insert("", tk.END, values=(
                p.id, p.cliente.split()[0], p.sector[:12],
                PRIO[p.prioridad], p.peso, f"{p.valor:.0f}"
            ))
        self._show_result(f"QuickSort «{self.var_criterio.get()}» · {len(ordenados)} pedidos · {elapsed:.2f} ms")
        self.app.actualizar_mapa(pedidos_resaltados=ordenados[:6])
        self.app.set_info_mapa(f"QuickSort: {len(ordenados)} pedidos ordenados por {self.var_criterio.get()}")

    def _buscar_id(self):
        ob = OrdenacionBusqueda()
        ordenados = sorted(self.app.pedidos, key=lambda p: p.id)
        target = self.var_busq_id.get()
        t0 = time.perf_counter()
        resultado = ob.busqueda_binaria_por_id(ordenados, target)
        elapsed = (time.perf_counter() - t0) * 1000
        if resultado:
            self._show_result(f"✔ #{resultado.id} – {resultado.cliente} | {resultado.sector} | {elapsed:.4f} ms")
            self.app.actualizar_mapa(pedidos_resaltados=[resultado])
        else:
            self._show_result(f"✘ ID #{target} no encontrado", error=True)

    def _buscar_sector(self):
        ob = OrdenacionBusqueda()
        sector = self.var_busq_sec.get()
        resultados = ob.busqueda_por_sector(self.app.pedidos, sector)
        self._show_result(f"Sector «{sector}»: {len(resultados)} resultado(s) · IDs: {[p.id for p in resultados]}")
        self.app.actualizar_mapa(pedidos_resaltados=resultados)

    def _show_result(self, txt, error=False):
        c = self.app.COLORES
        bg = c["tag_red"] if error else c["tag_blue"]
        fg = c["tag_red_t"] if error else c["tag_blue_t"]
        self.res_frame.config(bg=bg)
        self.lbl_busq.config(text=txt, bg=bg, fg=fg)
        self.res_frame.pack(fill=tk.X, padx=12, pady=4)
