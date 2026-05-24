# Nodos: Zonas principales distribuidas en un lienzo de 100x100
# Centro: Plaza de Armas en (50, 50)
# +Y = Norte, -Y = Sur, +X = Este, -X = Oeste
NODOS = {
    "Plaza de Armas":       (50, 50),
    "San Cristóbal":        (50, 75), # Norte (Expandido hacia arriba)
    "San Blas":             (65, 70), # Noreste
    "Santa Ana":            (35, 65), # Noroeste
    "Plaza San Francisco":  (40, 45), # Suroeste (Cerca de la Plaza)
    "San Pedro / Mercado":  (30, 35), # Suroeste (Más alejado)
    "Belén":                (25, 20), # Suroeste profundo
    "Santiago":             (15, 15), # Extremo Suroeste
    "Coricancha":           (60, 35), # Sureste (Bajando por Av. El Sol)
    "Limaqpampa":           (70, 40), # Sureste (Hacia Av. de la Cultura)
    "Estación Wanchaq":     (65, 20), # Sureste profundo (Final Av. El Sol)
    "Wanchaq (Túpac Amaru)":(85, 30), # Este-Sureste (Distrito moderno)
    "Ttio":                 (95, 10), # Extremo Sureste (Siguiendo el valle)
}

# Aristas: (nodo_a, nodo_b, tiempo_caminando_minutos)
# Los tiempos de caminata se mantienen fieles a la realidad física y topográfica.
ARISTAS_BASE = [
    # Rutas desde la Plaza de Armas
    ("Plaza de Armas", "Plaza San Francisco", 4),
    ("Plaza de Armas", "Coricancha",          6),
    ("Plaza de Armas", "San Blas",            8),  # Subida
    ("Plaza de Armas", "San Cristóbal",      12),  # Subida muy empinada
    ("Plaza de Armas", "Santa Ana",          14),  # Subida muy empinada
    
    # Eje Noroeste - Suroeste (Sector San Pedro / Santiago)
    ("Plaza San Francisco", "San Pedro / Mercado", 3),
    ("San Pedro / Mercado", "Belén",               6),
    ("San Pedro / Mercado", "Santiago",            9),
    ("Belén", "Santiago",                          5),
    ("Santa Ana", "San Pedro / Mercado",          12),
    
    # Eje Centro - Sureste (Sector Inca/Colonial hacia lo moderno)
    ("Coricancha", "Limaqpampa",              4),
    ("Coricancha", "Estación Wanchaq",        6),
    ("Limaqpampa", "Wanchaq (Túpac Amaru)",  10),
    ("San Blas", "Limaqpampa",                8),
    
    # Eje Sureste (Distritos modernos)
    ("Estación Wanchaq", "Wanchaq (Túpac Amaru)", 8),
    ("Wanchaq (Túpac Amaru)", "Ttio",        15),
    ("Estación Wanchaq", "Ttio",             12),
]

def construir_grafo(calles_bloqueadas=None):
    bloqueadas = set()
    if calles_bloqueadas:
        for c in calles_bloqueadas:
            partes = c.split("-")
            if len(partes) == 2:
                bloqueadas.add((partes[0].strip(), partes[1].strip()))
                bloqueadas.add((partes[1].strip(), partes[0].strip()))
    grafo = {n: [] for n in NODOS}
    for a, b, w in ARISTAS_BASE:
        if (a, b) not in bloqueadas:
            grafo[a].append((b, w))
            grafo[b].append((a, w))
    return grafo