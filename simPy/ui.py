"""
UI VISUAL
=========
Dibuja el Capataz (figura geométrica), el Grid, los Agentes y sus Órdenes.
"""

import pygame
from typing import List
from manager import EstadoCelda, EstadoAgenteVisibilidad, MetricasSistema, OrdenCapataz, NivelRiesgo

# CONFIGURACIÓN VISUAL
CELL_SIZE = 50
MARGIN_TOP = 100 # Espacio para el Capataz
COLOR_BG = (30, 30, 30)
COLOR_GRID = (50, 50, 50)
COLOR_CAPATAZ = (255, 215, 0) # Dorado

# Colores de celdas
COLORS_RISK = {
    NivelRiesgo.SIN_DATOS: (40, 40, 40),
    NivelRiesgo.BAJO: (34, 139, 34),    # Verde bosque
    NivelRiesgo.MEDIO: (255, 165, 0),   # Naranja
    NivelRiesgo.ALTO: (255, 69, 0),     # Rojo naranja
    NivelRiesgo.CRITICO: (75, 0, 130)   # Indigo/Morado (GUSANO)
}

class AgenteUI:
    def __init__(self, grid_filas, grid_columnas):
        self.rows = grid_filas
        self.cols = grid_columnas
        self.width = grid_columnas * CELL_SIZE + 300 # Panel info
        self.height = grid_filas * CELL_SIZE + MARGIN_TOP
        
        self.screen = None
        self.running = True
        
        # Datos a renderizar
        self.celdas = []
        self.agentes = []
        self.metricas = None

    def inicializar_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sistema Capataz - Control de Jitomates")
        self.font = pygame.font.SysFont("Arial", 16)
        self.font_big = pygame.font.SysFont("Arial", 24, bold=True)
        self.clock = pygame.time.Clock()

    def actualizar(self, celdas: List[EstadoCelda], agentes: List[EstadoAgenteVisibilidad], metricas: MetricasSistema):
        self.celdas = celdas
        self.agentes = agentes
        self.metricas = metricas

    def loop(self):
        if not self.screen: self.inicializar_pygame()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(COLOR_BG)
            
            self._dibujar_capataz()
            self._dibujar_grid()
            self._dibujar_agentes()
            self._dibujar_panel()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()

    def _dibujar_capataz(self):
        """Dibuja la figura geométrica fija que representa al Capataz"""
        cx, cy = self.width // 2, 50
        # Triángulo (El Ojo)
        puntos = [(cx, cy - 30), (cx - 30, cy + 20), (cx + 30, cy + 20)]
        pygame.draw.polygon(self.screen, COLOR_CAPATAZ, puntos)
        pygame.draw.circle(self.screen, (0,0,0), (cx, cy), 10) # Pupila
        
        # Texto del Capataz
        txt = self.font_big.render("EL CAPATAZ", True, COLOR_CAPATAZ)
        self.screen.blit(txt, (cx - 50, cy + 25))

    def _dibujar_grid(self):
        start_x = 20
        start_y = MARGIN_TOP
        
        # Fondo base grid
        for r in range(self.rows):
            for c in range(self.cols):
                rect = (start_x + c*CELL_SIZE, start_y + r*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2)
                pygame.draw.rect(self.screen, COLORS_RISK[NivelRiesgo.SIN_DATOS], rect)

        # Celdas con datos
        for celda in self.celdas:
            rect = (start_x + celda.y*CELL_SIZE, start_y + celda.x*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2)
            color = COLORS_RISK.get(celda.nivel_riesgo, (100,100,100))
            
            pygame.draw.rect(self.screen, color, rect)
            
            # Si hay frutos listos y no hay gusano
            if celda.listo_para_cosechar and not celda.tiene_gusano:
                pygame.draw.circle(self.screen, (255, 0, 0), (rect[0]+CELL_SIZE//2, rect[1]+CELL_SIZE//2), 8) # Tomate
            
            # Si hay GUSANO
            if celda.tiene_gusano:
                pygame.draw.line(self.screen, (0,0,0), (rect[0], rect[1]), (rect[0]+CELL_SIZE, rect[1]+CELL_SIZE), 3)
                pygame.draw.line(self.screen, (0,0,0), (rect[0]+CELL_SIZE, rect[1]), (rect[0], rect[1]+CELL_SIZE), 3)

    def _dibujar_agentes(self):
        start_x = 20
        start_y = MARGIN_TOP
        
        for ag in self.agentes:
            cx = start_x + ag.y * CELL_SIZE + CELL_SIZE // 2
            cy = start_y + ag.x * CELL_SIZE + CELL_SIZE // 2
            
            # Cuerpo agente
            color_ag = (100, 200, 255)
            if ag.orden_actual == OrdenCapataz.ABANDONAR: color_ag = (100, 100, 100) # Gris si abandona
            pygame.draw.circle(self.screen, color_ag, (cx, cy), 15)
            
            # VISUALIZACIÓN DE ÓRDENES (En la cabeza)
            texto_orden = ""
            color_texto = (255, 255, 255)
            
            if ag.orden_actual == OrdenCapataz.PARAR:
                texto_orden = "STOP"
                color_texto = (255, 50, 50)
                # Dibujar simbolo pausa
                pygame.draw.rect(self.screen, (255,0,0), (cx-5, cy-5, 4, 10))
                pygame.draw.rect(self.screen, (255,0,0), (cx+1, cy-5, 4, 10))
                
            elif ag.orden_actual == OrdenCapataz.ABANDONAR:
                texto_orden = "ABORT"
                color_texto = (255, 255, 0)
                
            elif ag.orden_actual == OrdenCapataz.CONTINUAR:
                # Solo mostrar ID si trabaja normal
                texto_id = self.font.render(str(ag.id), True, (0,0,0))
                self.screen.blit(texto_id, (cx-4, cy-8))

            if texto_orden:
                surf = self.font_big.render(texto_orden, True, color_texto)
                # Dibujar arriba de la cabeza
                self.screen.blit(surf, (cx - 20, cy - 35))

    def _dibujar_panel(self):
        x = self.cols * CELL_SIZE + 40
        y = MARGIN_TOP
        
        if not self.metricas: return
        
        lines = [
            f"MÉTRICAS SISTEMA",
            f"----------------",
            f"Tiempo: {self.metricas.tiempo_transcurrido:.1f}s",
            f"Explorado: {self.metricas.celdas_exploradas}",
            f"Cosechado: {self.metricas.frutos_cosechados} 🍅",
            f"Gusanos Detectados: {self.metricas.amenazas_gusano} 🐛",
            f"",
            f"LEYENDA:",
            f"Triángulo: Capataz",
            f"Círculo Azul: Recolector",
            f"Cuadro Morado: GUSANO",
            f"Punto Rojo: Jitomate Listo"
        ]
        
        for i, line in enumerate(lines):
            t = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(t, (x, y + i*25))

    def detener(self):
        self.running = False