# Nodos: Zonas principales distribuidas en un lienzo de 100x100
# Centro: Plaza de Armas en (50, 50)
# +Y = Norte, -Y = Sur, +X = Este, -X = Oeste
#
# AMPLIADO: de 13 a 22 nodos cubriendo más distritos de Cusco
# Nuevos sectores: Av. de la Cultura, UNSAAC, Huanchac, Larapa,
#                  Magisterio, Qosqo Mall / Real Plaza, San Sebastián, Poroy

NODOS = {
    # ── Centro histórico (originales) ────────────────────────────────────────
    "Plaza de Armas":          (50, 50),
    "San Cristóbal":           (50, 75),   # Norte, subida empinada
    "San Blas":                (65, 70),   # Noreste del centro
    "Santa Ana":               (35, 65),   # Noroeste, barrio histórico
    "Plaza San Francisco":     (40, 45),   # Suroeste cercano
    "San Pedro / Mercado":     (30, 35),   # Suroeste, mercado central
    "Belén":                   (25, 20),   # Suroeste profundo
    "Santiago":                (15, 15),   # Extremo Suroeste
    "Coricancha":              (60, 35),   # Sureste, Av. El Sol

    # ── Eje Av. de la Cultura / Wanchaq (originales) ─────────────────────────
    "Limaqpampa":              (70, 40),   # Inicio Av. de la Cultura
    "Estación Wanchaq":        (65, 20),   # Final Av. El Sol
    "Wanchaq (Túpac Amaru)":   (85, 30),   # Distrito moderno
    "Ttio":                    (95, 10),   # Extremo Sureste

    # ── NUEVOS NODOS ─────────────────────────────────────────────────────────
    "Av. de la Cultura":       (75, 35),   # Eje principal moderno
    "UNSAAC":                  (80, 42),   # Universidad Nacional
    "Huanchac":                (72, 22),   # Zona sur de Wanchaq
    "Magisterio":              (58, 28),   # Urb. Magisterio, entre Wanchaq y El Sol
    "Qosqo Mall / Real Plaza":  (88, 42),   # Centros comerciales modernos
    "San Sebastián":           (92, 55),   # Distrito San Sebastián
    "Larapa":                  (85, 62),   # Urbanización Larapa
    "Poroy":                   (20, 80),   # Noroeste, estación tren a Machu Picchu
    "Saylla":                  (75, 5),   # Sur, conocido por chicharrones
}

# Aristas: (nodo_a, nodo_b, tiempo_en_minutos)
# Tiempos estimados a pie / en moto para delivery urbano.
ARISTAS_BASE = [
    # ── Rutas desde Plaza de Armas ───────────────────────────────────────────
    ("Plaza de Armas", "Plaza San Francisco",    4),
    ("Plaza de Armas", "Coricancha",             6),
    ("Plaza de Armas", "San Blas",               8),   # subida
    ("Plaza de Armas", "San Cristóbal",         12),   # subida muy empinada
    ("Plaza de Armas", "Santa Ana",             14),   # subida muy empinada
    ("Plaza de Armas", "Magisterio",            10),   # Av. El Sol hacia sur

    # ── Eje Noroeste–Suroeste (San Pedro / Santiago) ─────────────────────────
    ("Plaza San Francisco", "San Pedro / Mercado",  3),
    ("San Pedro / Mercado", "Belén",                6),
    ("San Pedro / Mercado", "Santiago",             9),
    ("Belén",               "Santiago",             5),
    ("Santa Ana",           "San Pedro / Mercado", 12),
    ("Santiago",            "Poroy",               20),  # carretera Noroeste

    # ── Eje Centro–Sureste (Av. El Sol → Av. de la Cultura) ──────────────────
    ("Coricancha",       "Limaqpampa",             4),
    ("Coricancha",       "Estación Wanchaq",        6),
    ("Coricancha",       "Magisterio",              5),
    ("Limaqpampa",       "Av. de la Cultura",       5),
    ("Limaqpampa",       "Wanchaq (Túpac Amaru)",  10),
    ("San Blas",         "Limaqpampa",              8),
    ("Magisterio",       "Estación Wanchaq",        7),
    ("Magisterio",       "Huanchac",                8),

    # ── Eje Sureste (distritos modernos) ─────────────────────────────────────
    ("Estación Wanchaq",      "Wanchaq (Túpac Amaru)",   8),
    ("Estación Wanchaq",      "Huanchac",                 6),
    ("Estación Wanchaq",      "Ttio",                    12),
    ("Wanchaq (Túpac Amaru)", "Ttio",                    15),
    ("Wanchaq (Túpac Amaru)", "Av. de la Cultura",        6),
    ("Wanchaq (Túpac Amaru)", "Qosqo Mall / Real Plaza",  8),

    # ── Nuevos ejes ───────────────────────────────────────────────────────────
    ("Av. de la Cultura",      "UNSAAC",                  5),
    ("Av. de la Cultura",      "Qosqo Mall / Real Plaza",  7),
    ("UNSAAC",                 "Qosqo Mall / Real Plaza",  6),
    ("UNSAAC",                 "San Sebastián",            8),
    ("Qosqo Mall / Real Plaza", "San Sebastián",           6),
    ("San Sebastián",          "Larapa",                   7),
    ("San Sebastián",          "Saylla",                  12),
    ("Larapa",                 "San Blas",                14),  # ruta alta
    ("Huanchac",               "Saylla",                  10),
    ("Ttio",                   "Saylla",                   8),
    ("Poroy",                  "San Cristóbal",           18),  # ruta noroeste
    ("Poroy",                  "Santa Ana",               22),
]


def construir_grafo(calles_bloqueadas=None):
    """
    Devuelve dict {nodo: [(vecino, peso), ...]}
    calles_bloqueadas: lista de strings "NodoA-NodoB"
    """
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