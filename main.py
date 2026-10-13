"""
Nombre: Main: Juego de la Vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Función principal que ejecuta una versión secuencial y paralela del juego de la vida.

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""
from models import Board
from sequential import SequentialGame
from parallel import ParallelGame
from gui import GameVisualizer
import random
import copy
import sys
from mpi4py import MPI

# Define comandos MPI
CMD_STEP = 1
CMD_EXIT = 0


# Headless worker para rangos distintos de 0
def run_worker_loop(engine_b):
    comm = MPI.COMM_WORLD

    
    while True:
        
        # Esperar al broadcast de rango 0
        cmd = comm.bcast(None, root=0)

        # Ejecución segun comandos
        if cmd == CMD_STEP:
            engine_b.step()
        elif cmd == CMD_EXIT:
            break


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    board = None

    # Rango 0 inicializa la configuración aletoria de tablero
    if rank == 0:
        board = Board(rows=20, cols=20)
        for row in range(board.rows):
            for col in range(board.cols):
                board.grid[row][col] = random.randint(0, 1)

    # 2. Todos los procesos instancian el engine
    engine_b = ParallelGame(board)

    if rank == 0:
        # Rango 0 crea el motor secuencial
        engine_a = SequentialGame(copy.deepcopy(board))

        # Inicia la GUI (sólo en rango 0)
        app = GameVisualizer(engine_a, engine_b, comm)
        app.run()

        # Todos los rangos terminan al cerrarse la aplicación
        comm.bcast(CMD_EXIT, root=0)
    else:
        # Los rangos distintos de 0 entran a un ciclo de trabajo sin GUI
        run_worker_loop(engine_b)
