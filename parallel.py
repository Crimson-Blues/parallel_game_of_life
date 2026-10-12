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
    [[2 2 2 0], [5 5 4 1]],
    [[4 5 4 2], [3 4 4 1]]
]"""
def readed_grid(grid, chunking):
    num_workers = len(chunking)
    results = Manager().list([None] * num_workers)
    processes = []

    for idx in range(num_workers):
        p = Process(target=readed_chunks, args=(grid, chunking[idx], results, idx))
        processes.append(p)

    for process in processes:
        process.start()
    for process in processes:
        process.join()

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
def readed_chunks(grid, target_rows, results, index):
    r0, r1 = target_rows
    readed_block = []
    
    for r in range(r0, r1):          # filas r0 .. r1-1
        list_row = []
        for c in range(len(grid[r])):
            list_row.append(count_neighbors(grid, r, c))
        readed_block.append(list_row)
    results[index] = readed_block



# ESCRITOR
# ENTRADA: matriz, fila comiendo, fila final (sin tomarla)
# SALIDA: el pedazo de matriz "resuelto"
def compute_band(grid, r0, r1):
    num_cols = len(grid[0])
    result = []

    for r in range(r0, r1):
        new_row = []
        for c in range(num_cols):
            neighbors = count_neighbors(grid, r, c)
            new_row.append(next_state(grid[r][c], neighbors))
        result.append(new_row)

    return result


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
        # matriz de la generación siguiente
        new_grid = [[0 for _ in range(4)] for _ in range(4)]
        chunking = create_bands(4, self.num_workers)
        readed_b = readed_grid(self.board, chunking)
        print(readed_b)