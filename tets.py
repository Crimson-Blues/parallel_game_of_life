"""
Verifica que ParallelGame da el mismo resultado que SequentialGame.
"""
import copy
import random

from models import Board
from sequential import SequentialGame
from parallel import ParallelGame


def random_board(rows, cols, seed):
    rng = random.Random(seed)  # semilla fija: la prueba es repetible
    board = Board(rows, cols)
    for r in range(rows):
        for c in range(cols):
            board.grid[r][c] = rng.randint(0, 1)
    return board


def compare(rows, cols, num_workers, generations, seed=42):
    board_seq = random_board(rows, cols, seed)
    board_par = copy.deepcopy(board_seq)  # copia independiente

    seq = SequentialGame(board_seq)
    par = ParallelGame(board_par, num_workers)

    for gen in range(1, generations + 1):
        seq.step()
        par.step()
        if seq.board.grid != par.board.grid:
            raise AssertionError(
                f"Difieren en la generación {gen} "
                f"({rows}x{cols}, {num_workers} workers)"
            )
    print(f"OK  {rows}x{cols}  workers={num_workers}  generaciones={generations}")


if __name__ == "__main__":
    # (filas, columnas, workers, generaciones)
    casos = [
        (10, 10, 1, 5),     # 1 worker: debe comportarse como el secuencial
        (10, 10, 2, 5),
        (10, 10, 3, 5),     # 10 filas entre 3: reparto no exacto
        (20, 15, 4, 5),     # tablero no cuadrado
        (50, 50, 8, 5),
        (100, 100, 7, 3),
    ]
    for rows, cols, workers, gens in casos:
        compare(rows, cols, workers, gens)

    print("\nTodas las pruebas pasaron: secuencial == paralelo")