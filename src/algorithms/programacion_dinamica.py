from typing import List, Tuple
from ..models.pedido import Pedido

class ProgramacionDinamica:
    def __init__(self, capacidad_max: float):
        self.capacidad_max = capacidad_max
        self.escala = 10
        self.W = int(capacidad_max * self.escala)
        self.tabla_dp = None
        self.log_pasos = []

    def resolver(self, pedidos: List[Pedido]) -> Tuple[List[Pedido], float, float]:
        n = len(pedidos)
        W = self.W
        pesos = [int(p.peso * self.escala) for p in pedidos]
        valores = [p.valor for p in pedidos]

        dp = [[0.0] * (W + 1) for _ in range(n + 1)]
        self.log_pasos.append(f"Capacidad: {self.capacidad_max}kg | {n} pedidos candidatos")
        self.log_pasos.append("Llenando tabla DP [n+1 × W+1]...\n")

        for i in range(1, n + 1):
            for w in range(W + 1):
                dp[i][w] = dp[i - 1][w]
                if pesos[i - 1] <= w:
                    candidato = dp[i - 1][w - pesos[i - 1]] + valores[i - 1]
                    if candidato > dp[i][w]:
                        dp[i][w] = candidato

        self.tabla_dp = dp

        seleccionados = []
        w = W
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                seleccionados.append(pedidos[i - 1])
                w -= pesos[i - 1]

        seleccionados.reverse()
        valor_total = sum(p.valor for p in seleccionados)
        peso_total = sum(p.peso for p in seleccionados)

        self.log_pasos.append(f"Valor máximo obtenido: S/{valor_total:.2f}")
        self.log_pasos.append(f"Peso total cargado:    {peso_total:.1f} / {self.capacidad_max} kg")
        self.log_pasos.append(f"Pedidos seleccionados ({len(seleccionados)}/{n}):")
        for p in seleccionados:
            self.log_pasos.append(f"  • #{p.id} {p.cliente:<15} peso={p.peso}kg  val=S/{p.valor:.2f}")

        return seleccionados, valor_total, peso_total