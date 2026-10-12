"""
Nombre: Modelos de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Lógica de base para implementación de versión simplificada
del Juego de la Vida empleando una orientación a objetos

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""
# Importación de librerias
import numpy as np


"""
Clase que representa un tablero del juego.
Parámetros:
- rows: Número de filas de tablero.
- cols: Número de columnas de tablero-
- grid: Arreglo 2D de 1's y 0's que almacena el estado actual de las
        celdas en el tablero
Métodos:
- init: Inicialización de tablero con arreglo 2D dimensional vacío de
        de filas y columnas especifícadas.
- set_board: Recibe un arreglo 2D y si sus dimensiones coinciden con las
            de la grilla original, reemplaca self.grid
- set_cell: Actualiza el valor de una celda en la grilla
- get_grid: Retorna referencia a grilla de tablero.
- get_grid_copy: Retorna una copia de la grilla del tablero.
- count_neighbors: Return the number of alive neighbors a given cell has.
"""
class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)] # Inicialización de tablero vació

    def set_grid(self, grid):
        if len(grid) == self.rows and len(grid[0]) == self.cols:
            self.grid = grid
        else:
            raise Exception("New board dimensions must match previous one")

    def set_cell(self, r, c, cell):
        try:
            self.grid[r][c] = cell
        except IndexError:
            raise Exception("Selected cell out of bounds of current board.")

    def get_grid(self):
        return self.grid

    def get_grid_copy(self):
        return self.grid.copy()

    def count_neighbors(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            count = 0
            for dr in (-1, 0, 1): # Vecinos de fila
                for dc in (-1, 0, 1): # Vecinos de columna
                    if dr == 0 and dc == 0:
                        continue # Saltar propia celda

                    # Dimensions de vecino a revisar
                    nr = r + dr
                    nc = c + dc

                    # Solamente contar vecinos al interior de la grilla
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        count += self.grid[nr][nc]  
            return count
        else:
            raise Exception("Selected cell out of bounds of current board.")