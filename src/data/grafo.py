 
import heapq
 
LAT_MIN = -13.5440
LAT_MAX = -13.4990
LON_MIN = -72.0050
LON_MAX = -71.9420
 
def gps_a_canvas(lat, lon):
    """Convierte GPS → (X, Y) canvas con norte arriba."""
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * 100
    y = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN) * 100
    return round(x, 1), round(y, 1)
 
# ── GPS verificados (Wikipedia / OpenStreetMap) ───────────────────────────────
_GPS = {
    # Centro histórico
    "Plaza de Armas":              (-13.5167, -71.9789),  # Wikipedia: 13°31'00"S 71°58'44"W
    "Qorikancha":                  (-13.5217, -71.9764),  # Av. El Sol / Santo Domingo
    "Plaza Regocijo":              (-13.5179, -71.9797),  # plaza contigua al suroeste
    "San Blas":                    (-13.5134, -71.9740),  # barrio artesanos, NE centro
    "San Cristóbal":               (-13.5100, -71.9790),  # capilla/mirador, colina norte
    "Santa Ana":                   (-13.5157, -71.9845),  # barrio noroeste, calle Saphy
 
    # Mercados / transporte
    "Mercado San Pedro":           (-13.5211, -71.9836),  # calle Cascaparo / Tupac Yupanqui
    "Puente":          (-13.5266, -71.9893),  # Av. Velasco Astete
    "Estación Wanchaq":            (-13.5282, -71.9676),  # Av. Pachacutec / Tullumayo
    "Poroy":                       (-13.4993, -72.0015),  # estación tren, noroeste
 
    # Distrito Santiago
    "Santiago":                    (-13.5350, -71.9940),  # plaza del distrito
 
    # Eje Av. El Sol / Av. de la Cultura
    "Limaqpampa":                  (-13.5232, -71.9727),  # plazoleta, inicio Av. Cultura
    "Av. Cultura / Magisterio":    (-13.5265, -71.9726),  # óvalo Magisterio
    "Óvalo Pachacutec":            (-13.5282, -71.9650),  # monumento Pachacutec, óvalo
    "Av. Cultura km1":             (-13.5251, -71.9660),  # intersección Av. Cultura este
    "UNSAAC":                      (-13.5220, -71.9607),  # campus universitario
    "Plaza Túpac Amaru":           (-13.5271, -71.9582),  # Wanchaq, plaza central
    "Real Plaza":                  (-13.5211, -71.9545),  # Real Plaza / Qosqo Mall
    "Ttio":                        (-13.5312, -71.9493),  # urb. Ttio
 
    # Distritos este / sur
    "San Sebastián":               (-13.5182, -71.9463),  # plaza principal San Sebastián
    "Larapa":                      (-13.5130, -71.9535),  # urb. Larapa, noreste
    "Saylla":                      (-13.5435, -71.9592),  # pueblo extremo sur
}
 
# Conversión GPS → canvas
NODOS = {nombre: gps_a_canvas(lat, lon) for nombre, (lat, lon) in _GPS.items()}
 
# ── Aristas (nodo_a, nodo_b, tiempo_min a ~20 km/h urbano) ──────────────────
ARISTAS_BASE = [
    # Centro histórico
    ("Plaza de Armas",        "Plaza Regocijo",              2),  # ~150 m
    ("Plaza de Armas",        "Qorikancha",                  5),  # Av. El Sol ~450 m
    ("Plaza de Armas",        "San Blas",                    8),  # Cuesta San Blas ~550 m
    ("Plaza de Armas",        "San Cristóbal",              12),  # Pumacurco ~800 m
    ("Plaza de Armas",        "Santa Ana",                  10),  # Calle Saphy ~700 m
    ("Plaza de Armas",        "Mercado San Pedro",           7),  # Cascaparo ~500 m
    ("Plaza Regocijo",        "Mercado San Pedro",           5),  # Calle Mantas ~350 m
    ("Plaza Regocijo",        "Santa Ana",                   8),  # Saphy ~600 m
    ("Santa Ana",             "San Cristóbal",               8),  # calles altas ~600 m
    ("San Blas",              "Qorikancha",                  9),  # Ahuacpinta ~650 m
    ("San Blas",              "San Cristóbal",               6),  # Pumacurco ~400 m
 
    # Suroeste (Santiago / Puente)
    ("Mercado San Pedro",     "Puente",          9),  # Av. del Ejército ~800 m
    ("Puente",    "Santiago",                    8),  # Av. del Ejército ~700 m
    ("Plaza Regocijo",        "Puente",         12),  # Calle Quera+Ejército ~1 km
    ("Santiago",              "Poroy",                      22),  # Carretera Poroy ~2.4 km
 
    # Eje Av. El Sol → Limaqpampa
    ("Qorikancha",            "Limaqpampa",                  4),  # Av. El Sol ~320 m
    ("Limaqpampa",            "Av. Cultura km1",             5),  # inicio Av. Cultura ~400 m
    ("Limaqpampa",            "Av. Cultura / Magisterio",    6),  # Av. Garcilaso ~480 m
 
    # Óvalo Magisterio / Wanchaq
    ("Av. Cultura / Magisterio", "Estación Wanchaq",         6),  # Av. Túpac Amaru ~500 m
    ("Av. Cultura / Magisterio", "Óvalo Pachacutec",         7),  # Av. Huanchac ~600 m
    ("Av. Cultura km1",       "Óvalo Pachacutec",            5),  # diagonal ~400 m
    ("Av. Cultura km1",       "UNSAAC",                      5),  # Av. Cultura este ~400 m
 
    # Eje Av. de la Cultura (moderno)
    ("UNSAAC",                "Real Plaza",                  6),  # Av. Cultura ~500 m
    ("UNSAAC",                "Plaza Túpac Amaru",           6),  # interna ~500 m
    ("Plaza Túpac Amaru",     "Real Plaza",                  7),  # Av. Cultura ~600 m
    ("Plaza Túpac Amaru",     "Óvalo Pachacutec",            6),  # Av. Túpac Amaru ~500 m
    ("Plaza Túpac Amaru",     "Ttio",                       12),  # Av. Túpac Amaru este ~1.1 km
 
    # Estación Wanchaq
    ("Estación Wanchaq",      "Óvalo Pachacutec",            5),  # Av. Huanchac ~400 m
    ("Estación Wanchaq",      "Plaza Túpac Amaru",           8),  # Av. Túpac Amaru ~650 m
    ("Estación Wanchaq",      "Ttio",                       14),  # Av. Industrial ~1.3 km
 
    # Este / San Sebastián
    ("Real Plaza",            "San Sebastián",               6),  # Vía Evitamiento ~500 m
    ("Real Plaza",            "Larapa",                      7),  # sube a Larapa ~600 m
    ("San Sebastián",         "Larapa",                      8),  # Vía 28G ~700 m
    ("Ttio",                  "San Sebastián",               9),  # Vía Evitamiento ~800 m
    ("Ttio",                  "Saylla",                      9),  # carretera sur ~850 m
    ("Óvalo Pachacutec",      "Saylla",                     11),  # Av. Huanchac sur ~1 km
    ("San Sebastián",         "Saylla",                     14),  # carretera sur ~1.3 km
 
    # Larapa
    ("Larapa",                "San Blas",                   18),  # ruta serrana ~1.7 km
 
    # Poroy
    ("Poroy",                 "San Cristóbal",              22),  # ruta noroeste ~2.2 km
    ("Poroy",                 "Santa Ana",                  18),  # carretera bajada ~1.8 km
]
 
 
def construir_grafo(calles_bloqueadas=None):
    """
    Devuelve dict {nodo: [(vecino, tiempo_min), ...]}
    calles_bloqueadas: lista de strings 'NodoA-NodoB'
    """
    bloqueadas = set()
    if calles_bloqueadas:
        for c in calles_bloqueadas:
            partes = [p.strip() for p in c.split("-", 1)]
            if len(partes) == 2:
                bloqueadas.add((partes[0], partes[1]))
                bloqueadas.add((partes[1], partes[0]))
 
    grafo = {n: [] for n in NODOS}
    for a, b, w in ARISTAS_BASE:
        if (a, b) not in bloqueadas:
            grafo[a].append((b, w))
            grafo[b].append((a, w))
    return grafo
 
 
def dijkstra(grafo, origen, destino):
    """
    Dijkstra — camino más corto por tiempo.
    Devuelve (ruta: list[str], costo_min: float).
    Si no hay ruta devuelve ([], inf).
    """
    dist = {n: float("inf") for n in grafo}
    prev = {n: None for n in grafo}
    dist[origen] = 0
    heap = [(0, origen)]
 
    while heap:
        costo, nodo = heapq.heappop(heap)
        if nodo == destino:
            break
        if costo > dist[nodo]:
            continue
        for vecino, peso in grafo[nodo]:
            nd = costo + peso
            if nd < dist[vecino]:
                dist[vecino] = nd
                prev[vecino] = nodo
                heapq.heappush(heap, (nd, vecino))
 
    if dist[destino] == float("inf"):
        return [], float("inf")
 
    ruta, nodo = [], destino
    while nodo:
        ruta.append(nodo)
        nodo = prev[nodo]
    return list(reversed(ruta)), dist[destino]
