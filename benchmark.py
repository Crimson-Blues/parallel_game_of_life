"""
Nombre: Benchmark del juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-12
Descripción: Compara el tiempo por generación de los motores secuencial y
paralelos (sin GUI) y calcula speedup y eficiencia.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
import copy
import os
import platform
import time
import multiprocessing as mp

from sequential import SequentialGame
from parallel import ParallelGame
from parallel_pool import ParallelPoolGame, step_rows
from tets import random_board

SIZES = [50, 100, 250, 500, 1000] # Lados de los tableros (cuadrados) de la tabla 1
SCALING_SIZE = 500                # Lado del tablero de la prueba de escalabilidad
GENERATIONS = 3                   # Generaciones medidas por motor (después de 1 de calentamiento)
SEED = 42                         # Semilla fija: todos los motores parten del mismo tablero
NUM_CORES = os.cpu_count()


"""
Mismo kernel de parallel_pool.py pero sin procesos. Es la línea base justa
para el Pool: la diferencia de tiempos es solo efecto del paralelismo.
"""
class OptimizedSequentialGame:
    def __init__(self, board):
        self.board = board

    def step(self):
        zero_row = [0] * self.board.cols
        self.board.set_grid(step_rows([zero_row] + self.board.grid + [zero_row]))


# TIEMPO PROMEDIO POR GENERACIÓN (ms)
def time_engine(engine):
    engine.step() # Calentamiento
    start = time.perf_counter()
    for _ in range(GENERATIONS):
        engine.step()
    return (time.perf_counter() - start) * 1000 / GENERATIONS


def close_engine(engine):
    if hasattr(engine, "close"):
        engine.close()


# TABLA 1: tiempo por generación según el tamaño del tablero
def benchmark_sizes():
    print(f"\nTABLA 1: ms por generación ({NUM_CORES} workers)")
    print(f"{'Tablero':>11} | {'Secuencial':>10} | {'Sec. opt.':>10} | {'Par. Manager':>12} | {'Par. Pool':>10} "
          f"| {'S Manager':>9} | {'S Pool':>7} | {'S Pool*':>7}")

    for size in SIZES:
        board = random_board(size, size, SEED)
        engines = {
            "Secuencial": SequentialGame(copy.deepcopy(board)),
            "Sec. opt.": OptimizedSequentialGame(copy.deepcopy(board)),
            "Par. Manager": ParallelGame(copy.deepcopy(board), NUM_CORES),
            "Par. Pool": ParallelPoolGame(copy.deepcopy(board), NUM_CORES),
        }
        times = {name: time_engine(engine) for name, engine in engines.items()}

        # Todos hicieron las mismas generaciones desde el mismo tablero
        reference = engines["Secuencial"].board.grid
        for name, engine in engines.items():
            if engine.board.grid != reference:
                raise AssertionError(f"{name} difiere del secuencial en {size}x{size}")
            close_engine(engine)

        print(f"{f'{size}x{size}':>11} | {times['Secuencial']:10.1f} | {times['Sec. opt.']:10.1f} "
              f"| {times['Par. Manager']:12.1f} | {times['Par. Pool']:10.1f} "
              f"| {times['Secuencial'] / times['Par. Manager']:8.2f}x "
              f"| {times['Secuencial'] / times['Par. Pool']:6.2f}x "
              f"| {times['Sec. opt.'] / times['Par. Pool']:6.2f}x", flush=True)

    print("S Manager / S Pool: speedup contra el secuencial original (incluye la mejora del kernel).")
    print("S Pool*: speedup del Pool contra el mismo kernel sin procesos (solo efecto del paralelismo).")


# TABLA 2: escalabilidad según el número de workers
def benchmark_scaling():
    workers_list = []
    workers = 1
    while workers < NUM_CORES:
        workers_list.append(workers)
        workers *= 2
    workers_list.append(NUM_CORES)

    print(f"\nTABLA 2: escalabilidad en {SCALING_SIZE}x{SCALING_SIZE}")
    print(f"{'Motor':>12} | {'Workers':>7} | {'ms/gen':>8} | {'Speedup':>8} | {'Eficiencia':>10}")

    board = random_board(SCALING_SIZE, SCALING_SIZE, SEED)
    for name, engine_class in (("Par. Manager", ParallelGame), ("Par. Pool", ParallelPoolGame)):
        base_time = None
        for workers in workers_list:
            engine = engine_class(copy.deepcopy(board), workers)
            elapsed = time_engine(engine)
            engine.close()

            if base_time is None:
                base_time = elapsed # T1: el mismo motor con 1 worker
            speedup = base_time / elapsed
            print(f"{name:>12} | {workers:>7} | {elapsed:8.1f} | {speedup:7.2f}x | {speedup / workers:10.0%}", flush=True)

    print("Speedup = T1 / Tp (mismo motor con 1 worker) | Eficiencia = Speedup / workers")


if __name__ == "__main__":
    print(f"Python {platform.python_version()} | núcleos: {NUM_CORES} | "
          f"método de arranque: {mp.get_start_method()} | generaciones medidas: {GENERATIONS}")
    benchmark_sizes()
    benchmark_scaling()
