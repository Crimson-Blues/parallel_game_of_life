"""
Nombre: Motor paralelo de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Cálculo paralelo de la siguiente generación del juego.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
from sequential import next_state
from multiprocessing import Process, Manager
from itertools import chain


# LECTOR DE CELULA    
# ENTRADAS: Tablero, fila de la celula y columna de la celula
# SALIDAS: Número de células vivas que rodean a la célula
def count_neighbors(grid, r, c):
    num_rows = len(grid)
    num_cols = len(grid[0])
    count = 0

    for dr in (-1, 0, 1): # Vecinos de fila
        for dc in (-1, 0, 1): # Vecinos de columna
            if dr == 0 and dc == 0:
                continue # Saltar propia celda

            # Dimensions de vecino a revisar
            nr = r + dr
            nc = c + dc

            # Solamente contar vecinos al interior de la grilla
            if 0 <= nr < num_rows and 0 <= nc < num_cols:
                count += grid[nr][nc]  

    return count


# LECTOR DE TABLERO PARALELO
# ENTRADAS = 
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
def count_grid(grid, chunking):
    with Manager() as manager:
        processes_results = manager.list([None] * len(chunking))
        processes = [Process(target=count_rows, args=(grid, band, processes_results, i))
                     for i, band in enumerate(chunking)]

        for process in processes:
            process.start()
        for process in processes:
            process.join()
            if process.exitcode != 0:
                raise RuntimeError(f"Un proceso falló (exitcode={process.exitcode})")

        # NORMALIZAR: aplana un nivel
        results = list(chain.from_iterable(processes_results[:]))
        return results


# LEER POR BLOQUE
# ENTRADAS: Bloque por leer, y lista de resultados con su index para modificar
# SALIDAS: Bloque leido
"""
EJEMPLO DE ENTRADA
grid =
[
    [1 1 0 0],
    [0 1 0 0],
    [1 1 1 0],
    [1 1 0 1]
]
target_rows = [0, 2]

EJEMPLO DE SALIDA
results[index]=
[
    [2 2 2 0], 
    [5 5 4 1]
]
"""
def count_rows(grid, target_rows, results, index):
    r0, r1 = target_rows
    readed_block = []
    
    for r in range(r0, r1):          # filas r0 .. r1-1
        list_row = []
        for c in range(len(grid[r])):
            list_row.append(count_neighbors(grid, r, c))
        readed_block.append(list_row)
    results[index] = readed_block


#LECTOR DE LOS BLOQUES RESULTANTES DE readed_chunks
#ENTRADAS: recibe el tablero para saber cuales son las celular vivas, e lchunking y el resultado de haber leido los chunks
#SALIDA: los bloques con las nuevas celulas 
def grid_next_state(grid, chunking, readed_block):
    with Manager() as manager:
        processes_results = manager.list([None] * len(chunking))
        processes = [Process(target=rows_next_state, args=(grid[r0:r1], readed_block[r0:r1], processes_results, i))
                    for i, (r0, r1) in enumerate(chunking)]
        
        for process in processes:
            process.start()
        for process in processes:
            process.join()
            if process.exitcode != 0:
                raise RuntimeError(f"Un proceso falló (exitcode={process.exitcode})")

        # NORMALIZAR: aplana un nivel
        results = list(chain.from_iterable(processes_results[:]))
        
        return results


def rows_next_state(grid, block, results, index):
    cells = []

    for r in range(len(block)):
        new_row =[]
        for c in range(len(block[0])):
            new_cell = next_state(grid[r][c], block[r][c])
            new_row.append(new_cell)
        cells.append(new_row)
    results[index] = cells


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

    def step(self):
        grid = self.board.grid
        chunking = create_bands(self.board.rows, self.num_workers)
        counts = count_grid(grid, chunking)
        new_grid = grid_next_state(grid, chunking, counts)
        self.board.set_grid(new_grid)