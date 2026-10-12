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
    NUM_WORKERS = 10
    
    board = Board(rows=70 , cols=70)
    # Random board
    for row in range(board.rows):
        for col in range(board.cols):
            board.grid[row][col] = random.randint(0, 1) # Valor aleatorio de celda

    engine_a = SequentialGame(board)
    engine_b = ParallelGame(copy.deepcopy(board), 10)

    app = GameVisualizer(engine_a, engine_b)
    app.run()
