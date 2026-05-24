from typing import List, Tuple, Dict, Set

class Backtracking:
    def __init__(self, grafo: Dict):
        self.grafo = grafo
        self.todas_rutas: List[Tuple[List[str], float]] = []
        self.mejor_costo = float('inf')
        self.log_pasos = []
        self.nodos_explorados = 0

    def encontrar_rutas(self, origen: str, destino: str,
                         max_rutas: int = 50) -> Tuple[List[str], float]:
        self.todas_rutas = []
        self.mejor_costo = float('inf')
        self.nodos_explorados = 0
        self.log_pasos = []

        if origen not in self.grafo or destino not in self.grafo:
            self.log_pasos.append(f"ERROR: '{origen}' o '{destino}' no existe en el mapa.")
            return [], float('inf')

        self.log_pasos.append(f"Buscando rutas: {origen} → {destino}")
        self.log_pasos.append(f"Nodos en el mapa: {list(self.grafo.keys())}\n")

        visitados = set()
        self._backtrack(origen, destino, visitados, [origen], 0.0, max_rutas)

        if not self.todas_rutas:
            self.log_pasos.append("❌ No existe ninguna ruta entre los nodos dados.")
            return [], float('inf')

        self.todas_rutas.sort(key=lambda x: x[1])
        mejor_ruta, mejor_costo = self.todas_rutas[0]

        self.log_pasos.append(f"\nTotal de rutas encontradas: {len(self.todas_rutas)}")
        self.log_pasos.append(f"Nodos explorados: {self.nodos_explorados}")
        self.log_pasos.append(f"\n🏆 MEJOR RUTA ({mejor_costo} min):")
        self.log_pasos.append(" → ".join(mejor_ruta))
        self.log_pasos.append(f"\nTodas las rutas encontradas:")
        for i, (ruta, costo) in enumerate(self.todas_rutas[:10], 1):
            marca = "★" if i == 1 else " "
            self.log_pasos.append(f"  {marca} Ruta {i} ({costo} min): {' → '.join(ruta)}")
        if len(self.todas_rutas) > 10:
            self.log_pasos.append(f"  ... y {len(self.todas_rutas) - 10} ruta(s) más.")

        return mejor_ruta, mejor_costo

    def _backtrack(self, actual: str, destino: str, visitados: Set,
                   camino: List[str], costo: float, max_rutas: int):
        self.nodos_explorados += 1
        if actual == destino:
            self.todas_rutas.append((list(camino), costo))
            if costo < self.mejor_costo:
                self.mejor_costo = costo
                self.log_pasos.append(f"  Nueva mejor ruta: {' → '.join(camino)} ({costo} min)")
            return
        if len(self.todas_rutas) >= max_rutas:
            return
        visitados.add(actual)
        for vecino, peso in self.grafo.get(actual, []):
            if vecino not in visitados:
                if costo + peso < self.mejor_costo:
                    camino.append(vecino)
                    self._backtrack(vecino, destino, visitados,
                                    camino, costo + peso, max_rutas)
                    camino.pop()
        visitados.discard(actual)