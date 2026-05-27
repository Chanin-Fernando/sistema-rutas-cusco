import tkinter as tk
import time
from ...algorithms import ProgramacionDinamica
from ..base_tab import BaseTab

class PDTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "💼 Programación Dinámica",
                      "Knapsack 0/1 – carga óptima · O(n × W)")
        ctrl = self._ctrl_row(self.tab)
        self._label(ctrl, "Capacidad máx (kg):").pack(side=tk.LEFT)
        self.var_cap = tk.DoubleVar(value=15.0)
        tk.Spinbox(ctrl, from_=5, to=50, increment=0.5,
                   textvariable=self.var_cap, width=6,
                   bg=c["chip_bg"], fg=c["text"], font=("Segoe UI", 9),
                   relief=tk.FLAT, buttonbackground=c["chip_bg"]).pack(side=tk.LEFT, padx=6)
        self._boton(ctrl, "▶ Optimizar carga", self._ejecutar_pd).pack(side=tk.LEFT)
        self.txt_pd = self._text_area(self.tab)

    def _ejecutar_pd(self):
        cap = self.var_cap.get()
        pd = ProgramacionDinamica(cap)
        t0 = time.perf_counter()
        seleccionados, valor, peso = pd.resolver(self.app.pedidos)
        elapsed = (time.perf_counter() - t0) * 1000
        n = len(self.app.pedidos)
        lines = [
            f"── Knapsack 0/1 – Programación Dinámica ──",
            f"Capacidad: {cap} kg  |  {n} pedidos  |  Tiempo: {elapsed:.3f} ms", ""
        ]
        lines.extend(pd.log_pasos)
        lines.append(f"\n── Complejidad ──")
        lines.append(f"  DP:          O(n×W) = {n}×{int(cap*10)} = {n*int(cap*10)} ops")
        lines.append(f"  Fuerza Bruta: O(2^n) = {2**n:,} ops")
        lines.append(f"  Ahorro:       {(2**n - n*int(cap*10)):,} ops evitadas")
        self._actualizar_text(self.txt_pd, lines)
        self.app.actualizar_mapa(pedidos_resaltados=seleccionados)
        self.app.set_info_mapa(f"Knapsack: {len(seleccionados)} pedidos · S/{valor:.2f} · {peso:.1f} kg")
