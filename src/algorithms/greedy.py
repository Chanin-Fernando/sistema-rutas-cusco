from typing import List, Dict
from ..models.pedido import Pedido
from ..models.repartidor import Repartidor
from ..data.grafo import construir_grafo, dijkstra, NODOS


class AlgoritmoGreedy:
    def __init__(self, repartidores: List[Repartidor]):
        self.repartidores = repartidores
        self.carga_actual = {r.id: 0.0 for r in repartidores}
        self.log_pasos = []
        self._grafo = construir_grafo()  # grafo con tiempos reales

    def _nodo_mas_cercano(self, x: float, y: float) -> str:
        """Devuelve el nodo del grafo más cercano a las coordenadas (x, y)."""
        return min(NODOS, key=lambda n: (NODOS[n][0]-x)**2 + (NODOS[n][1]-y)**2)

    def _tiempo_real(self, origen_x, origen_y, pedido: Pedido) -> float:
        """
        Calcula el tiempo real de viaje desde (origen_x, origen_y)
        hasta el sector del pedido usando Dijkstra sobre el grafo.
        """
        nodo_origen  = self._nodo_mas_cercano(origen_x, origen_y)
        nodo_destino = pedido.sector if pedido.sector in self._grafo else \
                       self._nodo_mas_cercano(pedido.coord_x, pedido.coord_y)
        _, costo = dijkstra(self._grafo, nodo_origen, nodo_destino)
        return costo

    def asignar_pedidos(self, pedidos: List[Pedido]) -> tuple:
        asignaciones: Dict[int, List[Pedido]] = {r.id: [] for r in self.repartidores}
        sin_asignar = []

        for pedido in pedidos:
            mejor_rep   = None
            mejor_tiempo = float("inf")

            for rep in self.repartidores:
                capacidad_restante = rep.capacidad_max - self.carga_actual[rep.id]
                if capacidad_restante < pedido.peso:
                    continue
                # Tiempo real por grafo en lugar de distancia euclidiana
                tiempo = self._tiempo_real(rep.pos_x, rep.pos_y, pedido)
                if tiempo < mejor_tiempo:
                    mejor_tiempo = tiempo
                    mejor_rep    = rep

            if mejor_rep:
                asignaciones[mejor_rep.id].append(pedido)
                self.carga_actual[mejor_rep.id] += pedido.peso
                self.log_pasos.append(
                    f"✓ Pedido #{pedido.id} ({pedido.cliente}) → "
                    f"{mejor_rep.nombre} | tiempo_ruta={mejor_tiempo:.1f} min | "
                    f"carga={self.carga_actual[mejor_rep.id]:.1f}/{mejor_rep.capacidad_max} kg"
                )
            else:
                sin_asignar.append(pedido)
                self.log_pasos.append(
                    f"✗ Pedido #{pedido.id} ({pedido.cliente}) → SIN ASIGNAR "
                    f"(ningún repartidor con capacidad disponible)"
                )

        if sin_asignar:
            self.log_pasos.append(
                f"\n⚠ {len(sin_asignar)} pedido(s) sin asignar por falta de capacidad."
            )

        rutas = {}
        for rep in self.repartidores:
            pedidos_rep = asignaciones[rep.id]
            if not pedidos_rep:
                rutas[rep.id] = []
                continue
            rutas[rep.id] = self._vecino_mas_cercano_real(rep.pos_x, rep.pos_y, pedidos_rep)

        return asignaciones, rutas

    def _vecino_mas_cercano_real(self, ox: float, oy: float,
                                  pedidos: List[Pedido]) -> List[Pedido]:
        """Ordena los pedidos por tiempo de viaje real (Dijkstra), no euclidiana."""
        pendientes = list(pedidos)
        ruta = []
        cx, cy = ox, oy
        while pendientes:
            pendientes.sort(key=lambda p: self._tiempo_real(cx, cy, p))
            siguiente = pendientes.pop(0)
            ruta.append(siguiente)
            cx, cy = siguiente.coord_x, siguiente.coord_y
        return ruta