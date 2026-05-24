from typing import List, Dict, Tuple, Optional

class DivideYVenceras:
    def __init__(self, min_x=0, max_x=100, min_y=0, max_y=100):
        self.bounds = (min_x, max_x, min_y, max_y)
        self.cuadrantes = []
        self.log_pasos = []

    def segmentar(self, pedidos, profundidad: int = 0, max_prof: int = 2,
                  bounds: Tuple = None) -> List[Dict]:
        if bounds is None:
            bounds = self.bounds
        min_x, max_x, min_y, max_y = bounds
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        self.log_pasos.append(
            f"{'  ' * profundidad}Nivel {profundidad}: zona "
            f"({min_x:.0f},{min_y:.0f})→({max_x:.0f},{max_y:.0f}) "
            f"| {len(pedidos)} pedido(s)"
        )

        if profundidad >= max_prof or len(pedidos) <= 2:
            resultado = {"bounds": bounds, "pedidos": pedidos, "nivel": profundidad}
            self.cuadrantes.append(resultado)
            return [resultado]

        q1, q2, q3, q4 = [], [], [], []
        for p in pedidos:
            if p.coord_x <= mid_x and p.coord_y > mid_y:
                q1.append(p)
            elif p.coord_x > mid_x and p.coord_y > mid_y:
                q2.append(p)
            elif p.coord_x <= mid_x and p.coord_y <= mid_y:
                q3.append(p)
            else:
                q4.append(p)

        self.log_pasos.append(
            f"{'  ' * profundidad}  ↳ Divide: NO={len(q1)}, NE={len(q2)}, SO={len(q3)}, SE={len(q4)}"
        )

        resultados = []
        for quad, bnd in [
            (q1, (min_x, mid_x, mid_y, max_y)),
            (q2, (mid_x, max_x, mid_y, max_y)),
            (q3, (min_x, mid_x, min_y, mid_y)),
            (q4, (mid_x, max_x, min_y, mid_y)),
        ]:
            if quad:
                resultados.extend(self.segmentar(quad, profundidad + 1, max_prof, bnd))
        return resultados

    def asignar_repartidores(self, cuadrantes: List[Dict], repartidores) -> Dict:
        asignacion = {}
        for c in cuadrantes:
            min_x, max_x, min_y, max_y = c["bounds"]
            mejor = min(
                repartidores,
                key=lambda r: abs(r.pos_x - (min_x + max_x) / 2) +
                              abs(r.pos_y - (min_y + max_y) / 2)
            )
            asignacion[id(c)] = {"cuadrante": c, "repartidor": mejor}
        return asignacion