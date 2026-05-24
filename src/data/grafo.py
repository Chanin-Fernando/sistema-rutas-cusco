NODOS = {
    "Plaza de Armas":    (50, 50),
    "San Blas":          (55, 60),
    "Mercado Central":   (44, 48),
    "Wanchaq":           (60, 35),
    "San Cristóbal":     (50, 65),
    "Santa Clara":       (42, 44),
    "Santiago":          (30, 42),
    "Ttio":              (70, 55),
    "Huanchac":          (65, 28),
    "Belén":             (48, 53),
    "Limaqpampa":        (56, 44),
    "San Pedro":         (45, 42),
}

ARISTAS_BASE = [
    ("Plaza de Armas", "San Blas",         4),
    ("Plaza de Armas", "Mercado Central",  5),
    ("Plaza de Armas", "Belén",            3),
    ("Plaza de Armas", "Limaqpampa",       4),
    ("San Blas", "San Cristóbal",          5),
    ("San Blas", "Ttio",                   8),
    ("Mercado Central", "Santa Clara",     4),
    ("Mercado Central", "San Pedro",       3),
    ("Santa Clara", "Santiago",            7),
    ("San Pedro", "Santiago",              6),
    ("Wanchaq", "Limaqpampa",             6),
    ("Wanchaq", "Huanchac",               7),
    ("Wanchaq", "Ttio",                   5),
    ("Huanchac", "Ttio",                  6),
    ("Belén", "Limaqpampa",              2),
    ("Limaqpampa", "San Pedro",          4),
    ("San Cristóbal", "Belén",           6),
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