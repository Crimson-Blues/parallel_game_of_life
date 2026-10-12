"""
Nombre: GUI
Autores:
- Juan Diego Cárdenas Mejía - 2416437
- Samuel Banguero Ortega - 2418671
- Santiago Arias Rojas - 2416285
Fecha de Creación: 2026-10-10
Descripción: Interfaz Gráfica de Usuario para la visualización de iteracciones del juego
"""
import pygame
import sys
import time

# Color Palette (RGB)
COLOR_BG = (15, 15, 20)          # Dark background
COLOR_GRID = (30, 30, 40)        # Subtle grid lines
COLOR_ALIVE = (0, 255, 150)       # Neon green active cells
COLOR_TEXT = (220, 220, 220)      # White text
COLOR_ACCENT = (255, 90, 95)      # Accent highlight

class GameVisualizer:
    def __init__(self, sec_engine, par_engine, cell_size=12, fps=30, divider_width=20):
        self.sec_engine = sec_engine
        self.par_engine = par_engine
        self.sec_board = sec_engine.board
        self.par_board = par_engine.board
        self.drawing_grid = sec_engine.board.get_grid_copy()
        self.cell_size = cell_size
        self.target_fps = fps
        self.divider_width = divider_width

        # Dimensiones del Canvas
        self.board_rows = sec_engine.board.rows
        self.board_cols = sec_engine.board.cols
        self.width = self.sec_engine.board.cols * self.cell_size * 2 + divider_width # Extra para división
        self.height = self.sec_engine.board.rows * self.cell_size + 40  # Extra 40px for HUD toolbar

        # Inicializar PyGame
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Juego de la vida de Conway - Secuencial Vs Paralelo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 14, bold=True)

        # Estados iniciales de simulación
        self.is_running = False
        self.last_step_time_sec = 0.0
        self.last_step_time_par = 0.0
        self.is_drawing = True

        #Variables de tiempo
        self.sec_avg = 0.0
        self.par_avg = 0.0
        self.alpha = 0.05

    def handle_input(self):
        """Processes key presses and mouse interactions."""
        drawing_right_offset = self.width//4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.is_drawing: # Primer inicio de simulación
                        self.sec_board.set_grid(self.drawing_grid)
                        self.par_board.set_grid(self.drawing_grid)
                        self.is_drawing = False
                        self.is_running = True
                    else:
                        self.is_running = not self.is_running  # Play/Pause
                elif event.key == pygame.K_r and not self.is_drawing: # Reset
                    self.drawing_state()              
                if not self.is_running and self.is_drawing:
                    if event.key == pygame.K_c:
                        self.clear_board()                    # Limpiar grilla
                    elif event.key == pygame.K_d:
                        self.randomize_board()                # Grilla aleatoria
                elif event.key == pygame.K_RIGHT and not self.is_running:
                    self.step_simulation()                # Avance de único paso
                    self.draw_grids()

        # Click izquierdo para dibujar celdas
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and self.is_drawing:  # Left Click
            pos = pygame.mouse.get_pos()
            # Only draw inside the grid area (above HUD)
            if pos[1] < self.board_rows * self.cell_size:
                col = (pos[0] - drawing_right_offset)// self.cell_size
                row = pos[1] // self.cell_size
                if 0 <= row < self.board_rows and 0 <= col < self.board_cols:
                    self.drawing_grid[row][col] = 1

        elif mouse_pressed[2] and self.is_drawing:  # Click derecho para borrarlas
            pos = pygame.mouse.get_pos()
            if pos[1] < self.board_rows * self.cell_size:
                col = (pos[0]- drawing_right_offset) // self.cell_size
                row = pos[1] // self.cell_size
                if 0 <= row < self.board_rows and 0 <= col < self.board_cols:
                    self.drawing_grid[row][col] = 0

    # Una generación del tablero
    def step_simulation(self):
        start_sec = time.perf_counter()
        self.sec_engine.step()
        end_sec = time.perf_counter()
        sec_time = (end_sec - start_sec) * 1000
        self.last_step_time_sec = sec_time

        if self.sec_avg == 0.0:
            self.sec_avg = sec_time
        else:
            self.sec_avg = (self.alpha * sec_time) + ((1 - self.alpha) * self.sec_avg)

        start_par = time.perf_counter()
        self.par_engine.step()
        end_par = time.perf_counter()
        par_time = (end_par - start_par) * 1000
        self.last_step_time_par = par_time

        if self.par_avg == 0.0:
            self.par_avg = par_time
        else:
            self.par_avg = (self.alpha * par_time) + ((1 - self.alpha) * self.par_avg)

    def drawing_state(self):
         self.is_drawing = True
         self.is_running = False
         self.drawing_grid = self.sec_board.get_grid_copy()

    def clear_board(self):
        self.drawing_grid = [[0 for _ in range(self.board_cols)] for _ in range(self.board_rows)]
        self.is_running = False

    def randomize_board(self, density=0.2):
        import random
        self.drawing_grid = [
            [1 if random.random() < density else 0 for _ in range(self.board_cols)]
            for _ in range(self.board_rows)
        ]

    # Dibujar grillo inicial de dibujo
    def draw_drawing_grid(self):
            self.screen.fill(COLOR_BG)
            right_offset = self.width//4

            # Dibujar celdas activas
            for r in range(self.board_rows):
                for c in range(self.board_cols):
                    if self.drawing_grid[r][c] == 1:
                        rect = (
                            c * self.cell_size + right_offset,
                            r * self.cell_size,
                            self.cell_size - 1,  # 1px border spacing
                            self.cell_size - 1
                        )
                        pygame.draw.rect(self.screen, COLOR_ALIVE, rect)

    def draw_grids(self):
        """Renders grid cells and lines."""
        self.screen.fill(COLOR_BG)
        right_offset_x = self.cell_size * self.board_cols + self.divider_width

        # 1. Draw Active Cells
        for r in range(self.board_rows):
            for c in range(self.board_cols):
                if self.sec_board.grid[r][c] == 1:
                    rect = (
                        c * self.cell_size,
                        r * self.cell_size,
                        self.cell_size - 1,  # 1px border spacing
                        self.cell_size - 1
                    )
                    pygame.draw.rect(self.screen, COLOR_ALIVE, rect)

                if self.par_board.grid[r][c] == 1:
                                    rect = (
                                        c * self.cell_size + right_offset_x,
                                        r * self.cell_size,
                                        self.cell_size - 1,  # 1px border spacing
                                        self.cell_size - 1
                                    )
                                    pygame.draw.rect(self.screen, COLOR_ALIVE, rect)
    # Control en fase de dibujo
    def draw_drawing_hud(self):
            hud_rect = (0, self.board_rows * self.cell_size, self.width, 40)
            pygame.draw.rect(self.screen, (25, 25, 35), hud_rect)
            pygame.draw.line(self.screen, (50, 50, 65), (0, hud_rect[1]), (self.width, hud_rect[1]), 1)
    
            # Status & Benchmarks
            status_str = "RUNNING" if self.is_running else "PAUSED"
            status_color = COLOR_ALIVE if self.is_running else COLOR_ACCENT
            
    
            fps_curr = int(self.clock.get_fps())
            
            controls_text = "[SPACE] Empezar | [L-Click] Vivas | [R-Click] Muertas | [C] Limpia | [D] Random"
    
            txt_surface2 = self.font.render(controls_text, True, COLOR_TEXT)

            txt_rect = txt_surface2.get_rect()
            txt_rect.centerx = self.width // 2           # Alinear en X
            txt_rect.top = hud_rect[1] + 10            # Posición relativa en Y
    
            self.screen.blit(txt_surface2, txt_rect)

    # Dibuja separador entre recuadros de versión secuencial y paralela. 
    def draw_separator(self):
        # Coordenada x de divisor
        divider_x = self.board_cols * self.cell_size + (self.divider_width // 2)
        
        line_color = (60, 65, 80)  # Linea divisoria
        pygame.draw.line(
            self.screen,
            line_color,
            (divider_x, 0), # Desde inicio                      
            (divider_x, self.height), # Hasta top de pantalla
            width=2                                
        )

    def draw_running_hud(self):
        right_offset = self.board_cols * self.cell_size + self.divider_width
        hud_rect = (0, self.board_rows * self.cell_size, self.width, 40)
        pygame.draw.rect(self.screen, (25, 25, 35), hud_rect)
        pygame.draw.line(self.screen, (50, 50, 65), (0, hud_rect[1]), (self.width, hud_rect[1]), 1)

        # Status & Benchmarks
        status_str = "RUNNING" if self.is_running else "PAUSED"
        status_color = COLOR_ALIVE if self.is_running else COLOR_ACCENT
        
        
        info_text_sec = f"[Secuencial] | Paso: {self.last_step_time_sec:.2f}ms | Promedio : {self.sec_avg:.2f}ms"
        info_text_par = f"[Paralelo] | Paso: {self.last_step_time_par:.2f}ms | Promedio : {self.par_avg:.2f}ms"
        controls_text = "[SPACE] Play/Pause | [R] Reiniciar"

        txt_surface1 = self.font.render(info_text_sec, True, status_color)
        txt_surface2 = self.font.render(info_text_par, True, status_color)
        txt_surface3 = self.font.render(controls_text, True, COLOR_TEXT)

        self.screen.blit(txt_surface1, (10, hud_rect[1] + 4))
        self.screen.blit(txt_surface2, (10 + right_offset, hud_rect[1] + 4))
        self.screen.blit(txt_surface3, (10, hud_rect[1] + 20))
        self.draw_separator()

    def run(self):
        """Main Pygame application loop."""
        while True:
            self.handle_input()

            if self.is_running:
                self.step_simulation()
                self.draw_grids()
            elif self.is_drawing:
                self.draw_drawing_grid()
                self.draw_drawing_hud()
            
            if not self.is_drawing:
                self.draw_running_hud()
            
            

            pygame.display.flip()
            self.clock.tick(self.target_fps)