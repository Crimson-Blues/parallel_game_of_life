"""
Nombre: GUI
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias 
Fecha de Creación: 2026-10-10
Descripción: Interfaz Gráfica de Usuario para la visualización de iteracciones del juego

Curso: Infraestructuras Paralelas y Distribuidas

Código: 750023C
"""
import tkinter as tk

class GameVisualizer:
    def __init__(self, engine, cell_size=10):
        self.engine = engine
        self.cell_size = cell_size
        
        self.root = tk.Tk()
        self.root.title("Conway's Game of Life")
        
        self.canvas = tk.Canvas(
            self.root, 
            width=engine.board.cols * cell_size, 
            height=engine.board.rows * cell_size,
            bg="black"
        )
        self.canvas.pack()

    def update_frame(self):
        # 1. Advance state using chosen engine (Sequential or Parallel)
        self.engine.step()

        # 2. Render current matrix to canvas
        self.canvas.delete("all")
        for r in range(self.engine.board.rows):
            for c in range(self.engine.board.cols):
                if self.engine.board.grid[r][c] == 1:
                    x1 = c * self.cell_size
                    y1 = r * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="")

        self.root.after(50, self.update_frame)

    def run(self):
        self.update_frame()
        self.root.mainloop()