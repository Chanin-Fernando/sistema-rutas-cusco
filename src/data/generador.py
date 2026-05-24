import random
from ..models.pedido import Pedido
from ..models.repartidor import Repartidor
from .grafo import NODOS

SECTORES = list(NODOS.keys())

CLIENTES = [
    "Ana Torres", "Carlos Quispe", "María Huanca", "José Mamani",
    "Rosa Ccopa", "Luis Flores", "Sofía Puma", "Diego Ramos",
    "Elena Cusi", "Raúl Pacheco", "Carmen Inca", "Pedro Vargas",
    "Lucía Soto", "Héctor Cruz", "Nilda Pillco"
]

def generar_pedidos(n: int = 10) -> list:
    """Genera n pedidos de ejemplo con coordenadas reales del Cusco."""
    pedidos = []
    random.seed(42)
    for i in range(1, n + 1):
        sector = random.choice(SECTORES)
        cx, cy = NODOS[sector]
        cx += random.uniform(-5, 5)
        cy += random.uniform(-5, 5)
        pedidos.append(Pedido(
            id=i,
            cliente=random.choice(CLIENTES),
            sector=sector,
            coord_x=round(max(0, min(100, cx)), 1),
            coord_y=round(max(0, min(100, cy)), 1),
            prioridad=random.choice([1, 1, 2, 2, 2, 3]),
            peso=round(random.uniform(0.5, 10.0), 1),
            valor=round(random.uniform(20, 200), 2),
        ))
    return pedidos

def generar_repartidores() -> list:
    return [
        Repartidor(1, "Repartidor A", 50, 50, capacidad_max=20),
        Repartidor(2, "Repartidor B", 30, 40, capacidad_max=15),
        Repartidor(3, "Repartidor C", 70, 60, capacidad_max=25),
    ]