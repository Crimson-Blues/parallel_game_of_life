"""
Nombre: Motor paralelo de juego de la vida con Pool
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-12
Descripción: Cálculo paralelo de la siguiente generación del juego usando un
Pool de procesos persistente. Cada proceso cuenta los vecinos y escribe el
nuevo estado en el mismo paso, recibiendo solo su banda + 1 fila de halo.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
from sequential import next_state
from parallel import create_bands
from multiprocessing import Pool
from itertools import chain


# TABLA DE REGLAS: RULE[estado][vecinos] -> nuevo estado
# Se construye con next_state para que las reglas sigan definidas en un solo lugar
RULE = tuple(tuple(next_state(state, neighbors) for neighbors in range(9))
             for state in (0, 1))


# SIGUIENTE ESTADO DE UNA BANDA
# ENTRADAS: Banda con 1 fila de halo arriba y abajo
# SALIDAS: Filas de la banda en la siguiente generación
# Cuenta los vecinos y escribe el nuevo estado en el mismo paso
"""
EJEMPLO DE ENTRADA
rows =
[
    [0 0 0 0],  <- halo
    [1 1 0 0],
    [0 1 0 0],
    [1 1 1 0]   <- halo
]

EJEMPLO DE SALIDA
[
    [1 1 0 0],
    [0 0 0 0]
]
"""
def step_rows(rows):
    rows = [[0] + row + [0] for row in rows] # Borde de ceros a los lados
    num_cols = len(rows[0]) - 2
    new_rows = []

    # Ventana de 3 filas: la de arriba, la actual y la de abajo
    for up, mid, down in zip(rows, rows[1:], rows[2:]):
        new_row = [0] * num_cols
        for c in range(1, num_cols + 1):
            neighbors = (up[c - 1] + up[c] + up[c + 1] +
                         mid[c - 1] +          mid[c + 1] +
                         down[c - 1] + down[c] + down[c + 1])
            new_row[c - 1] = RULE[mid[c]][neighbors]
        new_rows.append(new_row)

    return new_rows


"""
Clase que implementa el cálculo paralelo con un Pool de procesos.
Parámetros:
- board: Objeto tablero que mantiene el estado actual del tablero de juego
- num_workers: Número de procesos del Pool
Métodos:
- init: Crea el Pool una sola vez para todas las generaciones.
- step: Calcula en paralelo la siguiente generación del tablero.
- close: Cierra el Pool y espera a sus procesos.
"""
class ParallelPoolGame:
    def __init__(self, board, num_workers):
        self.board = board
        self.num_workers = num_workers
        self.chunking = create_bands(board.rows, num_workers) # Las dimensiones del tablero no cambian
        self.pool = Pool(num_workers)

    def step(self):
        zero_row = [0] * self.board.cols
        rows = [zero_row] + self.board.grid + [zero_row] # Halo de ceros arriba y abajo
        tasks = [rows[r0:r1 + 2] for r0, r1 in self.chunking]

        # NORMALIZAR: pool.map devuelve los bloques en orden, se aplana un nivel
        new_grid = list(chain.from_iterable(self.pool.map(step_rows, tasks)))
        self.board.set_grid(new_grid)

    def close(self):
        self.pool.close()
        self.pool.join()
