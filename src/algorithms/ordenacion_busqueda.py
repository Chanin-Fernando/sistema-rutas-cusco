from typing import List, Optional
from ..models.pedido import Pedido

class OrdenacionBusqueda:
    """
    Módulo de ordenación (QuickSort) y búsqueda (Binaria).
    """

    @staticmethod
    def quicksort_pedidos(pedidos: List[Pedido], criterio: str = "prioridad") -> List[Pedido]:
        lista = list(pedidos)

        def clave(p: Pedido) -> float:
            if criterio == "prioridad":
                return p.prioridad
            elif criterio == "valor":
                return -p.valor
            elif criterio == "peso":
                return p.peso
            else:
                return p.distancia_a(50, 50)

        def _qsort(arr, lo, hi):
            if lo >= hi:
                return
            pivot = arr[hi]
            i = lo - 1
            for j in range(lo, hi):
                if clave(arr[j]) <= clave(pivot):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
            p = i + 1
            _qsort(arr, lo, p - 1)
            _qsort(arr, p + 1, hi)

        _qsort(lista, 0, len(lista) - 1)
        return lista

    @staticmethod
    def busqueda_binaria_por_id(pedidos_ordenados: List[Pedido], target_id: int) -> Optional[Pedido]:
        lo, hi = 0, len(pedidos_ordenados) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if pedidos_ordenados[mid].id == target_id:
                return pedidos_ordenados[mid]
            elif pedidos_ordenados[mid].id < target_id:
                lo = mid + 1
            else:
                hi = mid - 1
        return None

    @staticmethod
    def busqueda_por_sector(pedidos: List[Pedido], sector: str) -> List[Pedido]:
        return [p for p in pedidos if sector.lower() in p.sector.lower()]