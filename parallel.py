"""
Nombre: Motor paralelo de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Cálculo paralelo de la siguiente generación del juego.
Los 2 managers (uno por fase) y los procesos se crean una sola vez y se
reutilizan en todas las generaciones.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
from sequential import next_state
from multiprocessing import Process, Manager
from itertools import chain
import atexit

# LECTOR DE CELULA
# ENTRADAS: Tablero con borde de ceros, fila de la celula y columna de la celula
# SALIDAS: Número de células vivas que rodean a la célula
# Gracias al borde de ceros no hace falta revisar los límites de la grilla
def count_neighbors(grid, r, c):
    up, mid, down = grid[r - 1], grid[r], grid[r + 1]
    return (up[c - 1] + up[c] + up[c + 1] +
            mid[c - 1] +            mid[c + 1] +
            down[c - 1] + down[c] + down[c + 1])


# LECTOR DE TABLERO PARALELO
# ENTRADAS: Tablero, chunking y las colas de la fase de conteo
# SALIDAS: Conteo de vecinos de todo el tablero
# A cada proceso solo se le envía su banda + 1 fila de halo arriba y abajo
"""
EJEMPLO DE ENTRADA
chunking = [[0 2] [2 4]]
[
    [1 1 0 0],
    [0 1 0 0],
    [1 1 1 0],
    [1 1 0 1]
]
EJEMPLO DE SALIDA
[
    [2 2 2 0],
    [5 5 4 1],
    [4 5 4 2],
    [3 4 4 1]
]"""
def count_grid(grid, chunking, queues_list, results):
    zero_row = [0] * len(grid[0])
    rows = [zero_row] + grid + [zero_row] # Halo de ceros arriba y abajo
    return run_phase(queues_list, results, [(rows[r0:r1 + 2],) for r0, r1 in chunking])


# LEER POR BLOQUE
# ENTRADAS: Banda por leer con 1 fila de halo arriba y abajo
# SALIDAS: Bloque leido
"""
EJEMPLO DE ENTRADA (banda [0, 2] del tablero anterior)
rows =
[
    [0 0 0 0],  <- halo
    [1 1 0 0],
    [0 1 0 0],
    [1 1 1 0]   <- halo
]

EJEMPLO DE SALIDA
[
    [2 2 2 0],
    [5 5 4 1]
]
"""
def count_rows(rows):
    rows = [[0] + row + [0] for row in rows] # Borde de ceros a los lados
    num_cols = len(rows[0]) - 2

    return [[count_neighbors(rows, r, c) for c in range(1, num_cols + 1)]
            for r in range(1, len(rows) - 1)] # Sin las filas de halo


#LECTOR DE LOS BLOQUES RESULTANTES DE count_grid
#ENTRADAS: recibe el tablero para saber cuales son las celular vivas, el chunking, el resultado de haber leido los chunks y las colas de la fase de siguiente estado
#SALIDA: los bloques con las nuevas celulas
def grid_next_state(grid, chunking, readed_grid, tasks, results):
    return run_phase(tasks, results, [(grid[r0:r1], readed_grid[r0:r1])
                                      for r0, r1 in chunking])


def rows_next_state(grid_block, readed_grid_block):
    return [[next_state(cell, neighbors) for cell, neighbors in zip(grid_row, readed_row)]
            for grid_row, readed_row in zip(grid_block, readed_grid_block)]


# EJECUTAR UNA FASE
# ENTRADAS: Cola de tareas de cada proceso, cola de resultados y tarea de cada proceso
# SALIDAS: Resultados de todos los procesos aplanados en orden
# Esperar los N resultados funciona como barrera entre fases
def run_phase(tasks, results, payloads):
    for task_queue, payload in zip(tasks, payloads):
        task_queue.put(payload)

    blocks = [None] * len(payloads)
    for _ in payloads:
        index, block = results.get()
        if isinstance(block, Exception):
            raise RuntimeError(f"Un proceso falló (proceso={index})") from block
        blocks[index] = block

    # NORMALIZAR: aplana un nivel
    return list(chain.from_iterable(blocks))


# EJECUTAR UNA TAREA
# Si la tarea falla se envía la excepción como resultado para no bloquear al proceso principal
def run_task(function, args, results, index):
    try:
        results.put((index, function(*args)))
    except Exception as error:
        results.put((index, error))


# PROCESO PERSISTENTE
# ENTRADAS: Colas de la fase de conteo, colas de la fase de siguiente estado e index de la banda
# Vive toda la ejecución: en cada generación cuenta su banda y luego calcula su siguiente estado
def worker(count_queue, count_results, state_queue, state_results, index):
    while True:
        task = count_queue.get()
        if task is None:
            break # Señal de apagado
        run_task(count_rows, task, count_results, index)

        task = state_queue.get()
        if task is None:
            break # Apagado mientras esperaba la segunda fase (p. ej. tras un fallo)
        run_task(rows_next_state, task, state_results, index)


# HACER EL CHUNKING
# SALIDA: lista de parejas ((0, 10) (10, 20)...)
def create_bands(rows, num_workers):
    bands = []
    base = rows // num_workers
    extra =  rows % num_workers
    start = 0

    for i in range(num_workers):
        size = base + 1 if i<extra else base
        end =  start + size
        bands.append((start,end))
        start = end

    return bands

class ParallelGame:
    def __init__(self, board, num_workers):
        self.board = board
        self.num_workers = num_workers
        self.chunking = create_bands(board.rows, num_workers) # Las dimensiones del tablero no cambian

        # Manager 1: fase de conteo | Manager 2: fase de siguiente estado
        self.count_manager = Manager() # MECANISMO DE IPC (Inter Procecess Comunication)
        self.state_manager = Manager()
        self.count_tasks = [self.count_manager.Queue() for _ in range(num_workers)]
        self.count_results = self.count_manager.Queue()
        self.state_tasks = [self.state_manager.Queue() for _ in range(num_workers)]
        self.state_results = self.state_manager.Queue()

        # El proceso i siempre atiende la banda i
        self.processes = [Process(target=worker,
                                  args=(self.count_tasks[i], self.count_results,
                                        self.state_tasks[i], self.state_results, i),
                                  daemon=True)
                          for i in range(num_workers)]
        for process in self.processes:
            process.start()

        self.closed = False
        atexit.register(self.close) # Apagar procesos y managers al salir del programa

    def step(self):
        grid = self.board.grid
        counts = count_grid(grid, self.chunking, self.count_tasks, self.count_results)
        new_grid = grid_next_state(grid, self.chunking, counts, self.state_tasks, self.state_results)
        self.board.set_grid(new_grid)

    def close(self):
        if self.closed:
            return
        self.closed = True

        # Señal de apagado en ambas fases: cada proceso sale desde la que esté esperando
        for task_queue in self.count_tasks + self.state_tasks:
            task_queue.put(None)
        for process in self.processes:
            process.join(timeout=1)
            if process.is_alive():
                process.terminate()
        self.count_manager.shutdown()
        self.state_manager.shutdown()
