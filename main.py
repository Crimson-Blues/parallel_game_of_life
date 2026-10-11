"""
Nombre: Main: Juego de la Vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias 
Fecha de Creación: 2026-10-10
Descripción: Función principal que ejecuta una versión secuencial o paralela del juego de la vida.

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""
from models import Board
from sequential import SequentialGame
#from parallel import ParallelGame
from gui import GameVisualizer
import random
from parallel import ParallelGame   # descomentar

if __name__ == "__main__":

    MODE = "parallel"
    NUM_WORKERS = 4

    if MODE == "sequential":
        engine = SequentialGame(Board)
    elif MODE == "parallel":
        engine = ParallelGame(Board, num_workers=NUM_WORKERS)
    else:
        raise ValueError(f"Modo inválido: {MODE}")

    app = GameVisualizer(engine)
    app.run()
    engine.close() if MODE == "parallel" else None