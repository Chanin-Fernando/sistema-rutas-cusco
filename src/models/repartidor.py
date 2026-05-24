from dataclasses import dataclass, field
from typing import List
from .pedido import Pedido

@dataclass
class Repartidor:
    """Repartidor con posición y capacidad."""
    id: int
    nombre: str
    pos_x: float
    pos_y: float
    capacidad_max: float   # kg máximos que puede cargar
    pedidos_asignados: List[int] = field(default_factory=list)

    def distancia_a_pedido(self, p: 'Pedido') -> float:
        import math
        return math.sqrt((self.pos_x - p.coord_x) ** 2 + (self.pos_y - p.coord_y) ** 2)