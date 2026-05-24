import math
from dataclasses import dataclass

@dataclass
class Pedido:
    """Representa un pedido de entrega en Cusco."""
    id: int
    cliente: str
    sector: str
    coord_x: float     # longitud simplificada (0-100)
    coord_y: float     # latitud simplificada (0-100)
    prioridad: int     # 1=urgente, 2=normal, 3=baja
    peso: float        # kg
    valor: float       # soles
    entregado: bool = False

    def distancia_a(self, x: float, y: float) -> float:
        """Distancia euclidiana al punto (x, y)."""
        return math.sqrt((self.coord_x - x) ** 2 + (self.coord_y - y) ** 2)

    def __repr__(self):
        return (f"Pedido#{self.id} [{self.cliente}] sector={self.sector} "
                f"prio={self.prioridad} peso={self.peso}kg val=S/{self.valor:.2f}")