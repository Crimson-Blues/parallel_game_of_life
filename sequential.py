"""
Nombre: Motor secuencial de juego de la vida
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Cálculo secuencial de actualización de siguiente generación de juego, para un tablero dado. 

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""

# Implementación de reglas para siguiente generación
def next_state(current_state, neighbors):
    # Para célula viva
    if current_state == 1:
        if neighbors < 2:
            return 0 # Muerte por soledad
        elif 2 <= neighbors <= 3:
            return 1 # Mantiene viva
        else:
            return 0 # Muerte por sobrepoblación

    else: # Para célula muerta
        if neighbors == 3:
            return 1 # Revive si tiene 3 vecinos
        else:
            return 0 # Mantiene muerta
"""
Clase que implementa lógica secuencial de cálculo de siguiente generaciones del juego. 
Parámetros:
- board: Objeto tablero que mantiene el estado actual del tablero de juego
Métodos:
- init: Inicializa un motor de juego con un objeto tablero.
- step: Cálcula de forma secuencial la siguiente iteracción del tablero. 
"""
class SequentialGame:
    def __init__(self, board):
        self.board = board

    def step(self):
        new_grid = [[0 for _ in range(self.board.cols)] for _ in range(self.board.rows)]
        # Chequeo secuencial de todas las celdas con ciclos for clásicos
        
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                neighbors = self.board.count_neighbors(r, c)
                state = self.board.grid[r][c]

                # Actualización de estado de célula
                new_grid[r][c] = next_state(state, neighbors)

        # Tablero de nueva generación 
        self.board.set_grid(new_grid)