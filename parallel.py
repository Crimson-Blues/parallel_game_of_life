"""
Nombre: Motor paralelo de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Motor de cálculo paralelo de la siguiente generación del juego.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
import numpy as np
from mpi4py import MPI
from sequential import next_state

def count_neighbors_padded(padded_grid, r, c):
    """Helper counting 8-neighbors inside the local padded matrix view."""
    rows, cols = padded_grid.shape
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc

            # Con filas extras no es necesario chequeo por filas, solo columnas
            if 0 <= nc < cols:
                count += padded_grid[nr][nc]  
    
    return count

# TABLA DE REGLAS: RULE[estado][vecinos] -> nuevo estado
# Se construye con next_state para que las reglas sigan definidas en un solo lugar
RULE = tuple(tuple(next_state(state, neighbors) for neighbors in range(9))
             for state in (0, 1))


"""
Clase que implementa lógica secuencial de cálculo de siguiente generaciones del juego. 
Parámetros:
- board: Objeto tablero que mantiene el estado actual del tablero de juego
Métodos:
- init: Inicializa un motor de juego con un objeto tablero.
- step: Cálcula de forma secuencial la siguiente iteracción del tablero. 
"""
class ParallelGame:
    def __init__(self, board=None):
        # Inicialización de comunicador entre procesos
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        # Guardado de objeto board
        self.board = board  
        self.local_grid = None
        self.local_rows = 0
        self.cols = 0

        # Sync dimensions & scatter initial board across ranks
        self.split_board()

    def split_board(self):
        """Splits grid into horizontal bands and distributes them to processes."""
        if self.rank == 0: # Sólo proceso maestro tiene acceso a la totalidad del tablero
            if self.board is None:
                raise ValueError("Se debe inicializar objeto Board")
            full_grid = np.array(self.board.grid, dtype=np.uint8)
            total_rows, self.cols = full_grid.shape
        else:
            full_grid = None
            total_rows = 0
            self.cols = 0

        # Broadcast de dimensiones a todos los trabajadores
        total_rows = self.comm.bcast(total_rows, root=0)
        self.cols = self.comm.bcast(self.cols, root=0)

        # División de equitativa por filas
        base_rows = total_rows // self.size
        remainder = total_rows % self.size # Filas sobrantes
        
        # Asignación de filas sobrantes
        counts = [(base_rows + 1 if i < remainder else base_rows) * self.cols for i in range(self.size)] # Num de células a enviar a cada proceso
        displacements = [sum(counts[:i]) for i in range(self.size)] # Punto de inicio de cada chunk 
        
        self.local_rows = counts[self.rank] // self.cols
        self.local_grid = np.empty((self.local_rows, self.cols), dtype=np.uint8)

        # Repartir las sub-grillas a tráves de los procesos
        # Empleando vectorización
        self.comm.Scatterv([full_grid, counts, displacements, MPI.UINT8_T], 
                           self.local_grid, root=0)

    # Intercambia fila superior e inferior con procesos vecinos
    def _halo_exchange(self):
        # Fila de cima no tiene vecino de arriba
        top_neighbor = self.rank - 1 if self.rank > 0 else MPI.PROC_NULL
        # Última fila no tiene vecino de abajo
        bottom_neighbor = self.rank + 1 if self.rank < self.size - 1 else MPI.PROC_NULL

        # Buffers para mensajes recibidos
        ghost_top = np.zeros(self.cols, dtype=np.uint8)
        ghost_bottom = np.zeros(self.cols, dtype=np.uint8)

        # Enviar fila superior a vecino de arriba & recibir fila de fondo de vecino de abajo
        self.comm.Sendrecv(sendbuf=self.local_grid[0, :], dest=top_neighbor,
                          recvbuf=ghost_bottom, source=bottom_neighbor)

        # Enviar fila de abajo & recibir fila de arriba
        self.comm.Sendrecv(sendbuf=self.local_grid[-1, :], dest=bottom_neighbor,
                          recvbuf=ghost_top, source=top_neighbor)

        # Construir vista local
        padded_grid = np.vstack([ghost_top, self.local_grid, ghost_bottom])
        return padded_grid

    # Calcula una generación del tablero de forma paralela
    def step(self):
        # Intercambia y reciba filas extras
        padded = self._halo_exchange()

        # Grilla a llenar con valores
        new_local = np.empty_like(self.local_grid)
        
        for r in range(1, self.local_rows + 1):  # Offset de 1 por fila intercambiada, sin incluir última fila
            for c in range(self.cols):
                # Conteo de vecinos
                neighbors = count_neighbors_padded(padded, r, c)
                
                # Calcular nuevo valor actualizado
                current = padded[r, c]
                new_local[r - 1, c] = RULE[current][neighbors] 

        self.local_grid = new_local

        # Acumular totalidad de grilla en Rango 0
        all_counts = self.comm.gather(self.local_grid.size, root=0)
        
        if self.rank == 0:
            disps = [sum(all_counts[:i]) for i in range(self.size)]
            full_grid = np.empty((self.board.rows, self.cols), dtype=np.uint8)
        else:
            disps = None
            full_grid = None

        self.comm.Gatherv(self.local_grid, [full_grid, all_counts, disps, MPI.UINT8_T], root=0)

        if self.rank == 0:
            self.board.set_grid(full_grid)


