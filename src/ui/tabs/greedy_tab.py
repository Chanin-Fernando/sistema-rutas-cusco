import tkinter as tk
import time
from ...algorithms import AlgoritmoGreedy
from ..base_tab import BaseTab

class GreedyTab(BaseTab):
    def __init__(self, notebook, app):
        self.app = app
        self.tab = self._make_frame(notebook)
        self._crear_widgets()

    def _crear_widgets(self):
        self._seccion(self.tab, "⚡ Algoritmo Greedy",
                      "Vecino más cercano · O(n × m)")
        ctrl = self._ctrl_row(self.tab)
        self._boton(ctrl, "▶ Ejecutar asignación Greedy",
                    self._ejecutar_greedy).pack(side=tk.LEFT)
        self.txt_greedy = self._text_area(self.tab)

    def _ejecutar_greedy(self):
        g = AlgoritmoGreedy(self.app.repartidores)
        t0 = time.perf_counter()
        asignaciones, rutas = g.asignar_pedidos(self.app.pedidos)
        elapsed = (time.perf_counter() - t0) * 1000
        lines = [
            f"── Greedy: Asignación de Pedidos ──",
            f"Tiempo: {elapsed:.3f} ms  |  {len(self.app.pedidos)} pedidos  |  {len(self.app.repartidores)} repartidores",
            "",
        ]
        lines.extend(g.log_pasos)
        lines.append("\n── Rutas (Vecino más cercano) ──")
        todos = []
        for rep in self.app.repartidores:
            ruta = rutas[rep.id]
            lines.append(f"\n{rep.nombre}:")
            if not ruta:
                lines.append("  (sin pedidos asignados)")
                continue
            orden = " → ".join(f"#{p.id}" for p in ruta)
            lines.append(f"  Visita: {orden}")
            dist_total = 0.0; cx, cy = rep.pos_x, rep.pos_y
            for p in ruta:
                dist_total += p.distancia_a(cx, cy); cx, cy = p.coord_x, p.coord_y
            lines.append(f"  Distancia total: {dist_total:.1f} u")
            todos.extend(ruta)
        self._actualizar_text(self.txt_greedy, lines)
        primer_rep = self.app.repartidores[0]
        self.app.actualizar_mapa(pedidos_resaltados=rutas.get(primer_rep.id, []))
        self.app.set_info_mapa(f"Greedy: ruta de {primer_rep.nombre} en el mapa")
