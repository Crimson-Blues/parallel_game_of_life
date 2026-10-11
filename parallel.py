"""
Nombre: Motor paralelo de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias
Fecha de Creación: 2026-10-10
Descripción: Cálculo paralelo de la siguiente generación del juego.

Curso: Infraestructuras Paralelas y Distribuidas
Código: 750023C
"""
from sequential import next_state


def create_bansd)

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