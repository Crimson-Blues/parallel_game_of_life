"""
Nombre: Main: Juego de la Vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Función principal que ejecuta una versión secuencial o paralela del juego de la vida.

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""
from models import Board
from sequential import SequentialGame
from parallel import ParallelGame
from gui import GameVisualizer
import random
import copy

if __name__ == "__main__":
    MODE = "sequential"  # Opciones: "sequential" or "parallel"}
    NUM_WORKERS = 2
    
    board = Board(rows=50, cols=50)
    # Random board
    for row in range(board.rows):
        for col in range(board.cols):
            board.grid[row][col] = random.randint(0, 1) # Valor aleatorio de celda

    if MODE == "sequential":
        engine_a = SequentialGame(board)
        engine_b = SequentialGame(copy.deepcopy(board))

    if MODE == "parallel":
        engine = ParallelGame([[1, 1, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [1, 1, 0, 1]], NUM_WORKERS)

    app = GameVisualizer(engine_a, engine_b)
    app.run()
