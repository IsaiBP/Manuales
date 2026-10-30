# ============================================================
# BUSQUEDA EN DRIVEGUARD AI
# ============================================================
#
# Los temas de busqueda se aplican asi:
#
# El conductor esta en un nivel de riesgo (estado inicial) y
# queremos encontrar la SECUENCIA DE ACCIONES que lo lleve de
# regreso a NORMAL (estado objetivo).
#
# Cada accion es una ARISTA del grafo y tiene un costo: los
# puntos de riesgo que ayuda a reducir (dato ilustrativo).
#
#   Problema de busqueda  P = (S, A, s0, G, C)
#   S  = niveles de riesgo del conductor
#   A  = acciones correctivas con su costo
#   s0 = nivel que calcula evaluate() para la lectura actual
#   G  = NORMAL
#   C  = puntos que cada accion reduce
#
#   Algoritmos: BFS, DFS, UCS, Greedy y A*
#   Optimizacion: Hill Climbing y Algoritmo Genetico para
#   calibrar los umbrales con lecturas etiquetadas.
#
# Los costos son ilustrativos: no son minutos reales ni una
# eficacia validada de cada accion.
# ============================================================
import heapq
import random
from collections import deque
from dataclasses import replace

from core import Signals, Thresholds, evaluate

# ------------------------------------------------------------
# 1. ESPACIO DE BUSQUEDA: EL GRAFO DE ACCIONES
# ------------------------------------------------------------
# Formato:  estado: [(accion, estado destino, costo), ...]
#
# El dibujo del grafo dirigido:
#
#                 ventilar(1) ───────────┐
#   PRECAUCION ── pausa 15 min(2) ───────┤
#                 ignorar(3) ───┐        ▼
#                               ▼     ┌────────┐
#                          ┌──────────│ NORMAL │ (objetivo)
#                          │          └────────┘
#                          ▼               ▲
#                    ┌────────────┐        │
#                    │ALERTA ALTA │────────┤
#                    └────────────┘  pausa 15 min(2) → PRECAUCION
#                        │               cambiar conductor(4) → NORMAL
#                        └───────────────  detenerse y descansar(4) → NORMAL
#
# O sea, desde PRECAUCION hay 3 acciones posibles y desde
# ALERTA ALTA otras 3. NORMAL no tiene salidas: es la meta.
# ------------------------------------------------------------
grafo = {
    'NORMAL': [],
    'PRECAUCIÓN': [
        ('Ventilar el vehículo y beber agua', 'NORMAL', 1),
        ('Hacer una pausa de 15 minutos', 'NORMAL', 2),
        ('Ignorar las señales y continuar', 'ALERTA ALTA', 3),
    ],
    'ALERTA ALTA': [
        ('Hacer una pausa de 15 minutos', 'PRECAUCIÓN', 2),
        ('Cambiar de conductor', 'NORMAL', 4),
        ('Detenerse en un lugar seguro y descansar', 'NORMAL', 4),
    ],
}

GRAFO = grafo  # nombre usado por la ventana

# ------------------------------------------------------------
# 2. HEURISTICA h(n)
# ------------------------------------------------------------
# Estima cuantos puntos faltan, como minimo, para llegar a
# NORMAL. Es como la tabla "minutos caminando" de la practica:
# no es el costo real, solo una guia.
#
# Es admisible porque nunca se pasa del costo minimo real:
#   PRECAUCION -> NORMAL cuesta 1      → h = 1
#   ALERTA ALTA -> NORMAL cuesta 3     → h = 2  (mas barato por pausa)
# ------------------------------------------------------------
h = {
    'NORMAL': 0,
    'PRECAUCIÓN': 1,
    'ALERTA ALTA': 2,
}

HEURISTICA = h  # nombre usado por la ventana

OBJETIVO = 'NORMAL'


# ------------------------------------------------------------
# 3. AUXILIARES: COSTO DE UN CAMINO Y FORMATO DEL RESULTADO
# ------------------------------------------------------------
def costo_camino(camino, acciones):
    """Suma el costo de cada accion recorrida en el camino."""
    total = 0
    for i, accion in enumerate(acciones):
        origen, destino = camino[i], camino[i + 1]
        for a, d, c in grafo[origen]:
            if a == accion and d == destino:
                total += c
    return total


def resultado(algoritmo, camino, acciones, expandidos, registro):
    """Todos los algoritmos devuelven el mismo diccionario."""
    return {
        'algoritmo': algoritmo,
        'camino': camino,
        'acciones': acciones,
        'costo': costo_camino(camino, acciones) if camino else None,
        'aristas': len(camino) - 1,
        'expandidos': expandidos,
        'cantidad_expandidos': len(expandidos),
        'registro': registro,
    }


# ------------------------------------------------------------
# 4. BFS: BUSQUEDA EN ANCHURA
# ------------------------------------------------------------
# La cola guarda (estado, camino de estados, camino de acciones).
# Se extrae el primero que entro (FIFO), como en la practica
# con deque. Encuentra la ruta con MENOS ACCIONES, pero como
# las aristas tienen costos distintos, no garantiza menor costo.
# ------------------------------------------------------------
def bfs(inicio):
    cola = deque()
    cola.append((inicio, [inicio], []))
    visitados = set()
    expandidos, registro = [], []

    while cola:
        actual, camino, acciones = cola.popleft()
        if actual in visitados:
            continue
        visitados.add(actual)
        expandidos.append(actual)
        registro.append(f'BFS: se extrae {actual} de la cola.')

        if actual == OBJETIVO:
            return resultado('BFS', camino, acciones, expandidos, registro)

        for accion, destino, costo in grafo[actual]:
            if destino not in visitados:
                cola.append((destino, camino + [destino], acciones + [accion]))
                registro.append(f'  Se descubre {destino} con "{accion}" '
                                f'(costo={costo}).')
    return resultado('BFS', [], [], expandidos, registro)


# ------------------------------------------------------------
# 5. DFS: BUSQUEDA EN PROFUNDIDAD (RECURSIVA)
# ------------------------------------------------------------
# Igual que en la practica: visita el estado, pregunta si es el
# objetivo, y si no, entra por cada vecino con llamada recursiva.
# Si un camino no lleva a la meta, regresa (backtracking).
# ------------------------------------------------------------
def dfs(inicio):
    visitados = set()
    expandidos, registro = [], []

    def buscar(actual, camino, acciones):
        visitados.add(actual)
        expandidos.append(actual)
        registro.append(f'DFS: visitando {actual}.')

        if actual == OBJETIVO:
            return camino, acciones

        for accion, destino, _costo in grafo[actual]:
            if destino not in visitados:
                registro.append(f'  Se intenta "{accion}" hacia {destino}.')
                encontrado = buscar(destino, camino + [destino],
                                    acciones + [accion])
                if encontrado:
                    return encontrado
        return None

    encontrado = buscar(inicio, [inicio], [])
    if encontrado:
        camino, acciones = encontrado
    else:
        camino, acciones = [], []
    return resultado('DFS', camino, acciones, expandidos, registro)


# ------------------------------------------------------------
# 6. UCS: BUSQUEDA DE COSTO UNIFORME
# ------------------------------------------------------------
# Cola de prioridad (heapq) que saca primero el camino con
# menor costo acumulado g(n), como en p21grafo.py.
# Con costos positivos encuentra la ruta MAS BARATA.
# ------------------------------------------------------------
def ucs(inicio):
    pendientes = [(0, inicio, [inicio], [])]
    visitados = set()
    expandidos, registro = [], []

    while pendientes:
        costo_total, actual, camino, acciones = heapq.heappop(pendientes)
        if actual in visitados:
            continue
        visitados.add(actual)
        expandidos.append(actual)
        registro.append(f'UCS: se expande {actual} con g(n)={costo_total}.')

        if actual == OBJETIVO:
            return resultado('UCS', camino, acciones, expandidos, registro)

        for accion, destino, costo in grafo[actual]:
            if destino not in visitados:
                heapq.heappush(pendientes,
                               (costo_total + costo, destino,
                                camino + [destino], acciones + [accion]))
                registro.append(f'  {destino} por "{accion}": '
                                f'g(n)={costo_total + costo}.')
    return resultado('UCS', [], [], expandidos, registro)


# ------------------------------------------------------------
# 7. GREEDY: BUSQUEDA VORAZ PRIMERO EL MEJOR
# ------------------------------------------------------------
# Igual que GBFS.py: la cola ordena SOLO por h(n), el estado que
# "parece" mas cercano a la meta. No mira el costo recorrido,
# asi que puede elegir una ruta mas cara.
# ------------------------------------------------------------
def greedy(inicio):
    pendientes = [(h[inicio], inicio, [inicio], [])]
    visitados = set()
    expandidos, registro = [], []

    while pendientes:
        _h, actual, camino, acciones = heapq.heappop(pendientes)
        if actual in visitados:
            continue
        visitados.add(actual)
        expandidos.append(actual)
        registro.append(f'Greedy: se expande {actual} con h(n)={h[actual]}.')

        if actual == OBJETIVO:
            return resultado('Greedy', camino, acciones, expandidos, registro)

        for accion, destino, _costo in grafo[actual]:
            if destino not in visitados:
                heapq.heappush(pendientes,
                               (h[destino], destino,
                                camino + [destino], acciones + [accion]))
                registro.append(f'  {destino} por "{accion}": '
                                f'h(n)={h[destino]}.')
    return resultado('Greedy', [], [], expandidos, registro)


# ------------------------------------------------------------
# 8. A*: f(n) = g(n) + h(n)
# ------------------------------------------------------------
# Combina lo recorrido (g) con lo que falta (h). La cola saca
# el camino con menor f. Con heuristica admisible encuentra
# la ruta mas barata, igual que UCS, pero expande menos nodos.
# ------------------------------------------------------------
def astar(inicio):
    pendientes = [(h[inicio], 0, inicio, [inicio], [])]
    mejor_g = {inicio: 0}
    expandidos, registro = [], []

    while pendientes:
        f, g, actual, camino, acciones = heapq.heappop(pendientes)
        if g > mejor_g.get(actual):
            continue  # ya encontre este estado por un camino mas barato
        expandidos.append(actual)
        registro.append(f'A*: se expande {actual}: '
                        f'g={g}, h={h[actual]}, f={f}.')

        if actual == OBJETIVO:
            return resultado('A*', camino, acciones, expandidos, registro)

        for accion, destino, costo in grafo[actual]:
            nuevo_g = g + costo
            if nuevo_g < mejor_g.get(destino, 9999):
                mejor_g[destino] = nuevo_g
                heapq.heappush(pendientes,
                               (nuevo_g + h[destino], nuevo_g, destino,
                                camino + [destino], acciones + [accion]))
                registro.append(f'  {destino} por "{accion}": '
                                f'g={nuevo_g}, h={h[destino]}, '
                                f'f={nuevo_g + h[destino]}.')
    return resultado('A*', [], [], expandidos, registro)


ALGORITMOS = {
    'BFS': bfs,
    'DFS': dfs,
    'UCS': ucs,
    'Greedy': greedy,
    'A*': astar,
}


def plan_de_accion(nivel, algoritmo='A*'):
    """Resultado del algoritmo para un nivel de riesgo."""
    if nivel not in grafo:
        return None
    return ALGORITMOS[algoritmo](nivel)


# ============================================================
# 9. DATOS PARA CALIBRAR: LECTURAS ETIQUETADAS
# ============================================================
# Cada fila es (senales, nivel que deberia salir segun las
# reglas originales). Sirven para medir cuantos errores
# comete un conjunto de umbrales.
# ============================================================
LECTURAS_ETIQUETADAS = [
    (Signals(0.2, 16, 0, 5, True), 'NORMAL'),
    (Signals(0.0, 10, 0, 0, True), 'NORMAL'),
    (Signals(0.9, 20, 1, 15, True), 'NORMAL'),
    (Signals(1.1, 26, 2, 20, True), 'NORMAL'),
    (Signals(1.4, 20, 0, 10, True), 'PRECAUCIÓN'),
    (Signals(1.3, 20, 3, 10, True), 'ALERTA ALTA'),
    (Signals(0.5, 30, 0, 26, True), 'PRECAUCIÓN'),
    (Signals(0.0, 15, 3, 5, True), 'PRECAUCIÓN'),
    (Signals(2.6, 18, 0, 10, True), 'ALERTA ALTA'),
    (Signals(1.5, 28, 3, 30, True), 'ALERTA ALTA'),
    (Signals(0.4, 15, 0, 27, True), 'PRECAUCIÓN'),
    (Signals(3.0, 33, 4, 35, True), 'ALERTA ALTA'),
    (Signals(0.0, 0, 0, 0, False), 'SIN ROSTRO'),
    (Signals(2.0, 20, 0, 10, True), 'PRECAUCIÓN'),
]


def errores(umbrales=None, lecturas=LECTURAS_ETIQUETADAS):
    """Cuantas lecturas salen con el nivel equivocado."""
    cfg = umbrales or Thresholds()
    return sum(evaluate(s, cfg).level != esperado
               for s, esperado in lecturas)


# ------------------------------------------------------------
# 10. HILL CLIMBING: MEJORAR UN UMBRAL PASO A PASO
# ------------------------------------------------------------
# Idea: partir de un valor, probar sus vecinos (valor-1 y
# valor+1) y quedarse con el que tenga menos errores. Repetir
# mientras haya mejora. Es "subir la colina": siempre elegir
# lo mejor que tengo al lado.
# ------------------------------------------------------------
def hill_climbing_umbrales(base=None, campo='blinks_caution_per_minute',
                           inicio=None, minimo=10, maximo=45, paso=1):
    cfg = base or Thresholds()
    valor = inicio if inicio is not None else getattr(cfg, campo)
    mejor = errores(replace(cfg, **{campo: valor}))
    historial = [(valor, mejor)]

    while True:
        candidatos = []
        for nuevo in (valor - paso, valor + paso):
            if minimo <= nuevo <= maximo:
                e = errores(replace(cfg, **{campo: nuevo}))
                candidatos.append((e, nuevo))
        if not candidatos:
            break
        e, nuevo = min(candidatos, key=lambda c: (c[0], abs(c[1] - valor)))
        if e >= mejor:
            break  # tope de la colina: ningun vecino mejora
        valor, mejor = nuevo, e
        historial.append((valor, mejor))
    return replace(cfg, **{campo: valor}), mejor, historial


# ------------------------------------------------------------
# 11. ALGORITMO GENETICO: EVOLUCIONAR LOS SEIS UMBRALES
# ------------------------------------------------------------
# Cromosoma = la lista de 6 umbrales.
# Fitness = errores que comete (menor es mejor).
# Cada generacion: torneo de 3 para elegir padres, cruza de un
# punto para el hijo y mutacion con cierta probabilidad.
# ============================================================
GENES = [
    ('eye_closed_caution_seconds', 0.5, 2.0, 0.1),
    ('eye_closed_high_seconds', 1.5, 4.0, 0.1),
    ('blinks_caution_per_minute', 15, 40, 1),
    ('yawns_caution_per_minute', 1, 6, 1),
    ('head_tilt_caution_degrees', 10.0, 45.0, 1.0),
    ('high_score_min', 3, 7, 1),
]


def decodificar(genoma):
    """Convierte el cromosoma en un objeto Thresholds valido."""
    valores = {}
    for (campo, _min, _max, _res), gen in zip(GENES, genoma):
        valores[campo] = round(gen, 2)
    if valores['eye_closed_high_seconds'] <= valores['eye_closed_caution_seconds']:
        return None  # el umbral alto debe ser mayor que el de cautela
    return Thresholds(**valores)


def gen_aleatorio(rng):
    return [round(rng.uniform(minimo, maximo) / res) * res
            for _c, minimo, maximo, res in GENES]


def fitness(genoma):
    cfg = decodificar(genoma)
    return errores(cfg) if cfg else len(LECTURAS_ETIQUETADAS) + 1


def algoritmo_genetico_umbrales(poblacion=24, generaciones=30,
                                probabilidad_mutacion=0.2, semilla=1234):
    rng = random.Random(semilla)
    actual = [gen_aleatorio(rng) for _ in range(poblacion)]
    mejor = min(actual, key=fitness)
    historial = [fitness(mejor)]

    for _gen in range(generaciones):
        nueva = [mejor]  # elitismo: el mejor pasa directo
        while len(nueva) < poblacion:
            p1 = min(rng.sample(actual, 3), key=fitness)  # torneo de 3
            p2 = min(rng.sample(actual, 3), key=fitness)
            corte = rng.randrange(1, len(GENES))
            hijo = p1[:corte] + p2[corte:]
            if rng.random() < probabilidad_mutacion:
                i = rng.randrange(len(GENES))
                _c, minimo, maximo, res = GENES[i]
                hijo[i] = round(rng.uniform(minimo, maximo) / res) * res
            nueva.append(hijo)
        actual = nueva
        candidato = min(actual, key=fitness)
        if fitness(candidato) < fitness(mejor):
            mejor = candidato
        historial.append(fitness(mejor))
    return decodificar(mejor), fitness(mejor), historial


# ============================================================
# 12. PRUEBA RAPIDA EN CONSOLA
# ============================================================
if __name__ == '__main__':
    print('Estado inicial: ALERTA ALTA   Objetivo: NORMAL\n')
    for nombre, algoritmo in ALGORITMOS.items():
        r = algoritmo('ALERTA ALTA')
        print('----', nombre, '----')
        for linea in r['registro']:
            print(linea)
        if r['camino']:
            print('Ruta:', ' -> '.join(r['camino']),
                  '| Costo:', r['costo'],
                  '| Acciones:', ' ; '.join(r['acciones']))
        else:
            print('No se encontro ruta.')
        print()
