# Nodos: Zonas principales de Cusco en lienzo 100x100
# Centro: Plaza de Armas en (50, 50)
# +Y = Norte, -Y = Sur, +X = Este, -X = Oeste
#
# Coordenadas aproximadas basadas en la geografía real de Cusco.
# Distancias y tiempos estimados de OpenStreetMap / Google Maps (a pie o moto).

import heapq

NODOS = {
    # ── Centro histórico ──────────────────────────────────────────────────────
    "Plaza de Armas":          (50, 50),
    "San Cristóbal":           (50, 75),   # Norte, subida empinada
    "San Blas":                (65, 70),   # Noreste del centro
    "Santa Ana":               (35, 65),   # Noroeste, barrio histórico
    "Plaza San Francisco":     (40, 45),   # Suroeste cercano
    "San Pedro / Mercado":     (30, 35),   # Suroeste, mercado central
    "Belén":                   (25, 20),   # Suroeste profundo
    "Santiago":                (15, 15),   # Extremo Suroeste
    "Coricancha":              (60, 35),   # Sureste, Av. El Sol

    # ── Eje Av. de la Cultura / Wanchaq ───────────────────────────────────────
    "Limaqpampa":              (70, 40),   # Inicio Av. de la Cultura
    "Estación Wanchaq":        (65, 20),   # Final Av. El Sol
    "Wanchaq (Túpac Amaru)":   (85, 30),   # Distrito moderno
    "Ttio":                    (95, 10),   # Extremo Sureste

    # ── Nuevos nodos ──────────────────────────────────────────────────────────
    "Av. de la Cultura":       (75, 35),
    "UNSAAC":                  (80, 42),
    "Huanchac":                (72, 22),
    "Magisterio":              (58, 28),
    "Qosqo Mall / Real Plaza": (88, 42),
    "San Sebastián":           (92, 55),
    "Larapa":                  (85, 62),
    "Poroy":                   (20, 80),
    "Saylla":                  (75, 5),
}

# Aristas: (nodo_a, nodo_b, tiempo_min, distancia_metros)
# Tiempos y distancias aproximados de calles reales de Cusco.
# Fuente de referencia: Google Maps / OpenStreetMap modo caminando/moto.
ARISTAS_BASE = [
    # ── Desde Plaza de Armas ──────────────────────────────────────────────────
    ("Plaza de Armas",      "Plaza San Francisco",     4,   350),  # Calle Mantas
    ("Plaza de Armas",      "Coricancha",              6,   500),  # Av. El Sol
    ("Plaza de Armas",      "San Blas",                8,   550),  # Cuesta San Blas (empinada)
    ("Plaza de Armas",      "San Cristóbal",          12,   800),  # Subida muy empinada
    ("Plaza de Armas",      "Santa Ana",              14,   950),  # Calle Saphy
    ("Plaza de Armas",      "Magisterio",             10,   750),  # Av. El Sol hacia sur

    # ── Eje Suroeste (San Pedro / Santiago) ───────────────────────────────────
    ("Plaza San Francisco",  "San Pedro / Mercado",    3,   250),  # Calle Cascaparo
    ("San Pedro / Mercado",  "Belén",                  6,   500),  # Calle Belén
    ("San Pedro / Mercado",  "Santiago",               9,   800),  # Av. Ejército
    ("Belén",                "Santiago",               5,   400),  # Av. Ejército tramo corto
    ("Santa Ana",            "San Pedro / Mercado",   12,   950),  # Bajada Santa Ana
    ("Santiago",             "Poroy",                 20,  1800),  # Carretera Noroeste

    # ── Eje Centro–Sureste (Av. El Sol → Av. de la Cultura) ──────────────────
    ("Coricancha",           "Limaqpampa",             4,   350),  # Av. El Sol
    ("Coricancha",           "Estación Wanchaq",       6,   550),  # Av. El Sol completa
    ("Coricancha",           "Magisterio",             5,   420),  # Av. El Sol / Urb. Magisterio
    ("Limaqpampa",           "Av. de la Cultura",      5,   450),  # Inicio Av. de la Cultura
    ("Limaqpampa",           "Wanchaq (Túpac Amaru)", 10,   900),  # Av. Túpac Amaru
    ("San Blas",             "Limaqpampa",             8,   600),  # Calle Pumacurco
    ("Magisterio",           "Estación Wanchaq",       7,   600),  # Urb. Magisterio
    ("Magisterio",           "Huanchac",               8,   700),  # Av. Huanchac

    # ── Eje Sureste (distritos modernos) ──────────────────────────────────────
    ("Estación Wanchaq",     "Wanchaq (Túpac Amaru)",  8,   700),  # Av. Túpac Amaru
    ("Estación Wanchaq",     "Huanchac",               6,   500),  # Calle Huanchac
    ("Estación Wanchaq",     "Ttio",                  12,  1100),  # Av. Industrial
    ("Wanchaq (Túpac Amaru)","Ttio",                  15,  1400),  # Av. Túpac Amaru este
    ("Wanchaq (Túpac Amaru)","Av. de la Cultura",      6,   550),  # Conexión interna
    ("Wanchaq (Túpac Amaru)","Qosqo Mall / Real Plaza", 8,  700),  # Av. de la Cultura

    # ── Nuevos ejes ───────────────────────────────────────────────────────────
    ("Av. de la Cultura",    "UNSAAC",                 5,   400),  # Av. de la Cultura
    ("Av. de la Cultura",    "Qosqo Mall / Real Plaza", 7,  600),  # Av. de la Cultura este
    ("UNSAAC",               "Qosqo Mall / Real Plaza", 6,  500),  # Campus a mall
    ("UNSAAC",               "San Sebastián",           8,  700),  # Vía Evitamiento
    ("Qosqo Mall / Real Plaza","San Sebastián",         6,  550),  # Vía Evitamiento
    ("San Sebastián",        "Larapa",                  7,  600),  # Urb. Larapa
    ("San Sebastián",        "Saylla",                 12, 1100),  # Carretera sur
    ("Larapa",               "San Blas",               14, 1300),  # Ruta alta
    ("Huanchac",             "Saylla",                 10,  900),  # Av. Huanchac sur
    ("Ttio",                 "Saylla",                  8,  700),  # Carretera Ttio
    ("Poroy",                "San Cristóbal",          18, 1600),  # Ruta noroeste
    ("Poroy",                "Santa Ana",              22, 2000),  # Carretera Poroy
]


def construir_grafo(calles_bloqueadas=None, peso="tiempo"):
    """
    Devuelve dict {nodo: [(vecino, peso), ...]}

    peso: "tiempo"    → usa tiempo en minutos  (default)
          "distancia" → usa distancia en metros

    calles_bloqueadas: lista de strings "NodoA-NodoB"
    """
    bloqueadas = set()
    if calles_bloqueadas:
        for c in calles_bloqueadas:
            partes = c.split("-")
            if len(partes) == 2:
                bloqueadas.add((partes[0].strip(), partes[1].strip()))
                bloqueadas.add((partes[1].strip(), partes[0].strip()))

    idx_peso = 2 if peso == "tiempo" else 3   # índice en ARISTAS_BASE

    grafo = {n: [] for n in NODOS}
    for arista in ARISTAS_BASE:
        a, b = arista[0], arista[1]
        w = arista[idx_peso]
        if (a, b) not in bloqueadas:
            grafo[a].append((b, w))
            grafo[b].append((a, w))
    return grafo


def dijkstra(grafo, origen, destino):
    """
    Algoritmo de Dijkstra.
    Devuelve (ruta: list[str], costo: float)
    Si no hay ruta devuelve ([], inf).
    """
    dist = {n: float("inf") for n in grafo}
    prev = {n: None for n in grafo}
    dist[origen] = 0
    heap = [(0, origen)]

    while heap:
        costo_actual, nodo = heapq.heappop(heap)
        if nodo == destino:
            break
        if costo_actual > dist[nodo]:
            continue
        for vecino, peso in grafo[nodo]:
            nueva_dist = costo_actual + peso
            if nueva_dist < dist[vecino]:
                dist[vecino] = nueva_dist
                prev[vecino] = nodo
                heapq.heappush(heap, (nueva_dist, vecino))

    if dist[destino] == float("inf"):
        return [], float("inf")

    # Reconstruir camino
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = prev[nodo]
    ruta.reverse()
    return ruta, dist[destino]