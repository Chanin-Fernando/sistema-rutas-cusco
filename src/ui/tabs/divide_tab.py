import tkinter as tk
import time
from ...algorithms import DivideYVenceras
from ..base_tab import BaseTab

class DivideTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "🗺 Divide y Vencerás",
                      "Segmentación por cuadrantes · O(n log n)")
        ctrl = self._ctrl_row(self.tab)
        self._label(ctrl, "Profundidad máx:").pack(side=tk.LEFT)
        self.var_prof = tk.IntVar(value=2)
        tk.Spinbox(ctrl, from_=1, to=3, textvariable=self.var_prof,
                   width=3, bg=c["chip_bg"], fg=c["text"],
                   font=("Segoe UI", 9), relief=tk.FLAT,
                   buttonbackground=c["chip_bg"]).pack(side=tk.LEFT, padx=6)
        self._boton(ctrl, "▶ Segmentar mapa", self._ejecutar_divide).pack(side=tk.LEFT)
        self.txt_divide = self._text_area(self.tab)

    def _ejecutar_divide(self):
        dv = DivideYVenceras()
        t0 = time.perf_counter()
        cuadrantes = dv.segmentar(self.app.pedidos, max_prof=self.var_prof.get())
        elapsed = (time.perf_counter() - t0) * 1000
        asignacion = dv.asignar_repartidores(cuadrantes, self.app.repartidores)
        lines = [
            f"── Divide y Vencerás: Segmentación ──",
            f"Profundidad: {self.var_prof.get()}  |  Tiempo: {elapsed:.3f} ms",
            "", "── Árbol de Recursión ──"
        ]
        lines.extend(dv.log_pasos)
        lines.append("\n── Asignación de repartidores ──")
        for k, v in asignacion.items():
            bnd = v["cuadrante"]["bounds"]; rep = v["repartidor"]
            npeds = len(v["cuadrante"]["pedidos"])
            lines.append(f"  Cuadrante ({bnd[0]:.0f},{bnd[2]:.0f})→({bnd[1]:.0f},{bnd[3]:.0f}) | {npeds} ped → {rep.nombre}")
        self._actualizar_text(self.txt_divide, lines)
        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos, cuadrantes=cuadrantes)
        self.app.set_info_mapa(f"Divide y Vencerás: {len(cuadrantes)} cuadrantes")
