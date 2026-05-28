import tkinter as tk
import time
from ...algorithms import AlgoritmoGreedy
from ...data.grafo import construir_grafo, dijkstra, NODOS
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

    def _nodo_cercano(self, x, y):
        return min(NODOS, key=lambda n: (NODOS[n][0]-x)**2 + (NODOS[n][1]-y)**2)

    def _ejecutar_greedy(self):
        g = AlgoritmoGreedy(self.app.repartidores)
        t0 = time.perf_counter()
        asignaciones, rutas = g.asignar_pedidos(self.app.pedidos)
        elapsed = (time.perf_counter() - t0) * 1000

        lines = [
            f"── Greedy: Asignación de Pedidos ──",
            f"Tiempo de cómputo: {elapsed:.3f} ms  |  "
            f"{len(self.app.pedidos)} pedidos  |  "
            f"{len(self.app.repartidores)} repartidores",
            "",
        ]
        lines.extend(g.log_pasos)
        lines.append("\n── Rutas por repartidor (Vecino más cercano) ──")

        grafo = construir_grafo()

        for rep in self.app.repartidores:
            ruta = rutas[rep.id]
            lines.append(f"\n{rep.nombre}  (pos: nodo '{self._nodo_cercano(rep.pos_x, rep.pos_y)}'):")
            if not ruta:
                lines.append("  (sin pedidos asignados)")
                continue

            orden = " → ".join(f"#{p.id} {p.cliente.split()[0]}" for p in ruta)
            lines.append(f"  Orden de visita: {orden}")

            # Calcular tiempo total real por el grafo con Dijkstra
            tiempo_total = 0.0
            nodo_actual = self._nodo_cercano(rep.pos_x, rep.pos_y)
            detalle = []
            for p in ruta:
                nodo_destino = p.sector if p.sector in grafo else \
                               self._nodo_cercano(p.coord_x, p.coord_y)
                _, t = dijkstra(grafo, nodo_actual, nodo_destino)
                if t == float("inf"):
                    detalle.append(f"    #{p.id} → {nodo_destino}: sin ruta")
                else:
                    detalle.append(f"    #{p.id} {p.cliente.split()[0]} "
                                   f"→ {nodo_destino}: {t:.0f} min")
                    tiempo_total += t
                nodo_actual = nodo_destino

            lines.extend(detalle)
            lines.append(f"  ✓ Tiempo total de ruta: {tiempo_total:.0f} min  |  "
                         f"Carga: {g.carga_actual[rep.id]:.1f} kg")

        self._actualizar_text(self.txt_greedy, lines)
        primer_rep = self.app.repartidores[0]
        self.app.actualizar_mapa(pedidos_resaltados=rutas.get(primer_rep.id, []))
        self.app.set_info_mapa(f"Greedy: ruta de {primer_rep.nombre} en el mapa")