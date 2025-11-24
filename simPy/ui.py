"""
AGENTE UI - VISUALIZACIÓN PYGAME + RESUMEN TERMINAL
====================================================

Responsabilidades:
1. Visualizar simulación en tiempo real con Pygame
2. Mostrar grid del cultivo con colores
3. Mostrar agentes moviéndose
4. Mostrar métricas en pantalla
5. Generar resumen final en terminal
"""

import pygame
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque
import time

# Importar desde Manager
from manager import EstadoCelda, MetricasSistema, NivelRiesgo, EstadoMaduracion


# CONFIGURACIÓN DE PYGAME

class ConfigPygame:
    """Configuración visual de Pygame"""
    # Dimensiones
    CELL_SIZE = 60
    INFO_PANEL_WIDTH = 400
    HEADER_HEIGHT = 80
    FOOTER_HEIGHT = 60
    
    # Colores
    COLOR_BG = (20, 20, 30)
    COLOR_GRID = (40, 40, 50)
    COLOR_TEXT = (255, 255, 255)
    COLOR_TEXT_DIM = (150, 150, 160)
    
    # Colores de celdas según riesgo
    COLOR_SIN_EXPLORAR = (60, 60, 70)
    COLOR_BAJO_RIESGO = (46, 125, 50)
    COLOR_MEDIO_RIESGO = (255, 193, 7)
    COLOR_ALTO_RIESGO = (244, 67, 54)
    COLOR_CRITICO = (183, 28, 28)
    COLOR_COSECHA = (156, 39, 176)
    
    # Colores de agentes (uno para cada agente)
    COLORES_AGENTES = [
        (33, 150, 243),   # Azul
        (76, 175, 80),    # Verde
        (255, 152, 0),    # Naranja
        (233, 30, 99),    # Rosa
        (0, 188, 212),    # Cyan
    ]
    
    # Fuentes
    FONT_SIZE_TITLE = 28
    FONT_SIZE_SUBTITLE = 20
    FONT_SIZE_NORMAL = 16
    FONT_SIZE_SMALL = 14
    
    # Animación
    FPS = 30


# REGISTRO DE ACTIVIDAD

class RegistroActividad:
    """Mantiene un registro de eventos del sistema"""
    
    def __init__(self, max_eventos: int = 100):
        self.eventos = deque(maxlen=max_eventos)
        self.max_eventos = max_eventos
    
    def agregar_evento(self, tipo: str, mensaje: str, agente_id: int = None):
        """Agrega un evento al registro"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        evento = {
            'timestamp': timestamp,
            'tipo': tipo,
            'mensaje': mensaje,
            'agente_id': agente_id
        }
        self.eventos.append(evento)


# AGENTE UI CON PYGAME 

class AgenteUI:
    """
    Agente UI: Visualización con Pygame + Resumen en Terminal
    COMPATIBLE CON macOS - Ejecuta Pygame en el thread principal
    
    Características:
    - Visualización en tiempo real del grid
    - Agentes moviéndose por el cultivo
    - Código de colores para riesgos
    - Panel de métricas en vivo
    - Resumen final en terminal
    """
    
    def __init__(self, grid_filas: int = 10, grid_columnas: int = 10):
        """Inicializa el Agente UI con Pygame"""
        self.grid_filas = grid_filas
        self.grid_columnas = grid_columnas
        
        # Estado del sistema
        self.mapa_estados: Dict[tuple, EstadoCelda] = {}
        self.metricas: MetricasSistema = None
        self.posiciones_agentes: Dict[int, tuple] = {}
        
        # Registro de actividad
        self.registro = RegistroActividad(max_eventos=1000)
        
        # Control
        self.running = True
        self.pygame_iniciado = False
        
        # Referencias de Pygame
        self.screen = None
        self.clock = None
        
        print(f"[UI] ✅ Agente UI inicializado - Grid: {grid_filas}x{grid_columnas}")
    
    # INICIALIZACIÓN DE PYGAME (THREAD PRINCIPAL)
    
    def inicializar_pygame(self):
        """Inicializa Pygame en el thread principal (macOS compatible)"""
        if self.pygame_iniciado:
            return
        
        # Inicializar Pygame
        pygame.init()
        
        # Calcular dimensiones de ventana
        grid_width = self.grid_columnas * ConfigPygame.CELL_SIZE
        grid_height = self.grid_filas * ConfigPygame.CELL_SIZE
        
        self.window_width = grid_width + ConfigPygame.INFO_PANEL_WIDTH
        self.window_height = grid_height + ConfigPygame.HEADER_HEIGHT + ConfigPygame.FOOTER_HEIGHT
        
        # Crear ventana (en thread principal)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Sistema Multi-Agente - Monitoreo de Cultivo")
        
        # Crear reloj
        self.clock = pygame.time.Clock()
        
        # Cargar fuentes
        self.font_title = pygame.font.Font(None, ConfigPygame.FONT_SIZE_TITLE)
        self.font_subtitle = pygame.font.Font(None, ConfigPygame.FONT_SIZE_SUBTITLE)
        self.font_normal = pygame.font.Font(None, ConfigPygame.FONT_SIZE_NORMAL)
        self.font_small = pygame.font.Font(None, ConfigPygame.FONT_SIZE_SMALL)
        
        self.pygame_iniciado = True
    
    def ejecutar_loop_pygame(self):
        """
        Ejecuta el loop principal de Pygame
        DEBE llamarse desde el thread principal
        """
        if not self.pygame_iniciado:
            self.inicializar_pygame()
        
        # Loop principal de eventos y renderizado
        while self.running:
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Renderizar
            self._renderizar_pygame()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(ConfigPygame.FPS)
    
    def actualizar_frame(self):
        """
        Actualiza un solo frame (útil para control manual del loop)
        """
        if not self.pygame_iniciado:
            return
        
        # Procesar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Renderizar
        self._renderizar_pygame()
        
        # Actualizar pantalla
        pygame.display.flip()
        self.clock.tick(ConfigPygame.FPS)
    
    # RENDERIZADO PYGAME
    
    def _renderizar_pygame(self):
        """Renderiza toda la visualización en Pygame"""
        if not self.screen:
            return
        
        # Fondo
        self.screen.fill(ConfigPygame.COLOR_BG)
        
        # Header
        self._dibujar_header()
        
        # Grid del cultivo
        self._dibujar_grid()
        
        # Agentes
        self._dibujar_agentes()
        
        # Panel de información
        self._dibujar_panel_info()
        
        # Footer
        self._dibujar_footer()
    
    def _dibujar_header(self):
        """Dibuja el encabezado"""
        y_offset = 10
        
        # Título
        titulo = self.font_title.render("SISTEMA MULTI-AGENTE - MONITOREO DE CULTIVO", True, ConfigPygame.COLOR_TEXT)
        titulo_rect = titulo.get_rect(center=(self.window_width // 2, y_offset + 20))
        self.screen.blit(titulo, titulo_rect)
        
        # Tiempo y progreso
        if self.metricas:
            mins = int(self.metricas.tiempo_transcurrido // 60)
            segs = int(self.metricas.tiempo_transcurrido % 60)
            
            info = self.font_normal.render(
                f"Tiempo: {mins:02d}:{segs:02d}  |  Progreso: {self.metricas.porcentaje_analizado:.1f}%",
                True, ConfigPygame.COLOR_TEXT_DIM
            )
            info_rect = info.get_rect(center=(self.window_width // 2, y_offset + 50))
            self.screen.blit(info, info_rect)
        
        # Línea separadora
        pygame.draw.line(
            self.screen,
            ConfigPygame.COLOR_GRID,
            (0, ConfigPygame.HEADER_HEIGHT - 5),
            (self.window_width, ConfigPygame.HEADER_HEIGHT - 5),
            2
        )
    
    def _dibujar_grid(self):
        """Dibuja el grid del cultivo"""
        x_offset = 20
        y_offset = ConfigPygame.HEADER_HEIGHT + 20
        
        for i in range(self.grid_filas):
            for j in range(self.grid_columnas):
                x = x_offset + j * ConfigPygame.CELL_SIZE
                y = y_offset + i * ConfigPygame.CELL_SIZE
                
                # Obtener color de la celda
                color = self._obtener_color_celda(i, j)
                
                # Dibujar celda
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x, y, ConfigPygame.CELL_SIZE - 2, ConfigPygame.CELL_SIZE - 2),
                    border_radius=5
                )
                
                # Dibujar borde
                pygame.draw.rect(
                    self.screen,
                    ConfigPygame.COLOR_GRID,
                    (x, y, ConfigPygame.CELL_SIZE - 2, ConfigPygame.CELL_SIZE - 2),
                    1,
                    border_radius=5
                )
                
                # Mostrar número de frutos si hay
                celda = self.mapa_estados.get((i, j))
                if celda and celda.frutos_disponibles > 0:
                    texto = self.font_small.render(str(celda.frutos_disponibles), True, (255, 255, 255))
                    texto_rect = texto.get_rect(center=(x + ConfigPygame.CELL_SIZE // 2, y + ConfigPygame.CELL_SIZE // 2))
                    self.screen.blit(texto, texto_rect)
    
    def _obtener_color_celda(self, x: int, y: int) -> tuple:
        """Obtiene el color de una celda según su estado"""
        celda = self.mapa_estados.get((x, y))
        
        if not celda:
            return ConfigPygame.COLOR_SIN_EXPLORAR
        
        # Prioridad: cosecha > riesgo
        if celda.listo_para_cosechar:
            return ConfigPygame.COLOR_COSECHA
        
        if celda.nivel_riesgo == NivelRiesgo.CRITICO:
            return ConfigPygame.COLOR_CRITICO
        
        if celda.nivel_riesgo == NivelRiesgo.ALTO:
            return ConfigPygame.COLOR_ALTO_RIESGO
        
        if celda.nivel_riesgo == NivelRiesgo.MEDIO:
            return ConfigPygame.COLOR_MEDIO_RIESGO
        
        return ConfigPygame.COLOR_BAJO_RIESGO
    
    def _dibujar_agentes(self):
        """Dibuja los agentes en sus posiciones"""
        x_offset = 20
        y_offset = ConfigPygame.HEADER_HEIGHT + 20
        
        for agente_id, pos in self.posiciones_agentes.items():
            if pos:
                i, j = pos
                x = x_offset + j * ConfigPygame.CELL_SIZE + ConfigPygame.CELL_SIZE // 2
                y = y_offset + i * ConfigPygame.CELL_SIZE + ConfigPygame.CELL_SIZE // 2
                
                # Color del agente
                color = ConfigPygame.COLORES_AGENTES[(agente_id - 1) % len(ConfigPygame.COLORES_AGENTES)]
                
                # Dibujar círculo del agente
                pygame.draw.circle(self.screen, color, (x, y), 15)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 15, 2)
                
                # Dibujar ID del agente
                texto = self.font_small.render(str(agente_id), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(x, y))
                self.screen.blit(texto, texto_rect)
    
    def _dibujar_panel_info(self):
        """Dibuja el panel de información lateral"""
        x_offset = self.grid_columnas * ConfigPygame.CELL_SIZE + 40
        y_offset = ConfigPygame.HEADER_HEIGHT + 20
        
        if not self.metricas:
            return
        
        # Título del panel
        titulo = self.font_subtitle.render("MÉTRICAS", True, ConfigPygame.COLOR_TEXT)
        self.screen.blit(titulo, (x_offset, y_offset))
        y_offset += 40
        
        # Exploración
        self._dibujar_seccion_panel(
            "🔍 EXPLORACIÓN",
            [
                f"Celdas: {self.metricas.celdas_exploradas}/{self.metricas.celdas_totales}",
                f"Progreso: {self.metricas.porcentaje_analizado:.1f}%"
            ],
            x_offset, y_offset
        )
        y_offset += 80
        
        # Cosecha
        self._dibujar_seccion_panel(
            "🍅 COSECHA",
            [
                f"Frutos detectados: {self.metricas.frutos_totales_detectados}",
                f"Listos: {self.metricas.frutos_listos_cosecha}",
                f"Cosechados: {self.metricas.frutos_cosechados}"
            ],
            x_offset, y_offset
        )
        y_offset += 100
        
        # Riesgos
        self._dibujar_seccion_panel(
            "⚠️ RIESGOS",
            [
                f"Críticos: {self.metricas.celdas_criticas}",
                f"Alto riesgo: {self.metricas.celdas_alto_riesgo}",
                f"Tratamientos: {self.metricas.tratamientos_ordenados}"
            ],
            x_offset, y_offset
        )
        y_offset += 100
        
        # Agentes
        self._dibujar_seccion_panel(
            "🤖 AGENTES",
            [
                f"Total: {self.metricas.agentes_activos}",
                f"Explorando: {self.metricas.agentes_explorando}"
            ],
            x_offset, y_offset
        )
        y_offset += 80
        
        # Leyenda de colores
        y_offset += 20
        self._dibujar_leyenda(x_offset, y_offset)
    
    def _dibujar_seccion_panel(self, titulo: str, lineas: List[str], x: int, y: int):
        """Dibuja una sección del panel de información"""
        # Título de sección
        texto_titulo = self.font_normal.render(titulo, True, ConfigPygame.COLOR_TEXT)
        self.screen.blit(texto_titulo, (x, y))
        y += 25
        
        # Líneas de información
        for linea in lineas:
            texto = self.font_small.render(linea, True, ConfigPygame.COLOR_TEXT_DIM)
            self.screen.blit(texto, (x + 10, y))
            y += 20
    
    def _dibujar_leyenda(self, x: int, y: int):
        """Dibuja la leyenda de colores"""
        titulo = self.font_normal.render("LEYENDA", True, ConfigPygame.COLOR_TEXT)
        self.screen.blit(titulo, (x, y))
        y += 30
        
        leyenda = [
            (ConfigPygame.COLOR_BAJO_RIESGO, "Bajo riesgo"),
            (ConfigPygame.COLOR_MEDIO_RIESGO, "Medio riesgo"),
            (ConfigPygame.COLOR_ALTO_RIESGO, "Alto riesgo"),
            (ConfigPygame.COLOR_COSECHA, "Listo cosecha"),
        ]
        
        for color, texto in leyenda:
            # Dibujar cuadrado de color
            pygame.draw.rect(self.screen, color, (x, y, 20, 20), border_radius=3)
            pygame.draw.rect(self.screen, ConfigPygame.COLOR_GRID, (x, y, 20, 20), 1, border_radius=3)
            
            # Dibujar texto
            texto_render = self.font_small.render(texto, True, ConfigPygame.COLOR_TEXT_DIM)
            self.screen.blit(texto_render, (x + 30, y + 3))
            y += 30
    
    def _dibujar_footer(self):
        """Dibuja el pie de página"""
        y_offset = self.window_height - ConfigPygame.FOOTER_HEIGHT + 20
        
        # Línea separadora
        pygame.draw.line(
            self.screen,
            ConfigPygame.COLOR_GRID,
            (0, y_offset - 10),
            (self.window_width, y_offset - 10),
            2
        )
        
        # Instrucciones
        texto = self.font_small.render("Presiona ESC para salir", True, ConfigPygame.COLOR_TEXT_DIM)
        texto_rect = texto.get_rect(center=(self.window_width // 2, y_offset + 10))
        self.screen.blit(texto, texto_rect)
    
    # CALLBACK DESDE EL MANAGER
    
    def actualizar(self, estados: List[EstadoCelda], metricas: MetricasSistema):
        """
        Callback del Manager: recibe actualizaciones del sistema
        """
        # Actualizar estado interno
        for estado in estados:
            self.mapa_estados[(estado.x, estado.y)] = estado
        
        self.metricas = metricas
        
        # Registrar eventos importantes
        for estado in estados:
            if estado.listo_para_cosechar:
                self.registro.agregar_evento(
                    'cosecha',
                    f"Celda ({estado.x},{estado.y}): {estado.frutos_disponibles} frutos listos"
                )
            
            if estado.requiere_tratamiento:
                self.registro.agregar_evento(
                    'tratamiento',
                    f"Celda ({estado.x},{estado.y}): {estado.tipo_amenaza}"
                )
            
            if estado.nivel_riesgo == NivelRiesgo.CRITICO:
                self.registro.agregar_evento(
                    'alerta',
                    f"CRÍTICO en ({estado.x},{estado.y}): {estado.tipo_amenaza}"
                )
    
    def actualizar_posicion_agente(self, agente_id: int, x: int, y: int):
        """Actualiza la posición de un agente físico"""
        self.posiciones_agentes[agente_id] = (x, y)
    
    def detener(self):
        """Detiene la visualización"""
        self.running = False
        if self.pygame_iniciado:
            pygame.quit()
    
    # RESUMEN FINAL EN TERMINAL
    
    def mostrar_resumen_final(self):
        """Muestra un resumen final en la terminal"""
        # Detener Pygame
        self.detener()
        time.sleep(0.5)
        
        # Limpiar terminal
        os.system('clear' if os.name != 'nt' else 'cls')
        
        print("\n" + "="*90)
        print("✅ EXPLORACIÓN COMPLETADA - RESUMEN FINAL".center(90))
        print("="*90 + "\n")
        
        if self.metricas:
            mins = int(self.metricas.tiempo_transcurrido // 60)
            segs = int(self.metricas.tiempo_transcurrido % 60)
            
            print(f"⏱  Tiempo total: {mins:02d}:{segs:02d}\n")
            
            print("📊 RESULTADOS:")
            print(f"  • Celdas exploradas: {self.metricas.celdas_exploradas}/{self.metricas.celdas_totales}")
            print(f"  • Cobertura: {self.metricas.porcentaje_analizado:.1f}%")
            print(f"  • Frutos totales detectados: {self.metricas.frutos_totales_detectados}")
            print(f"  • Frutos listos para cosecha: {self.metricas.frutos_listos_cosecha}")
            print(f"  • 🍅 Frutos cosechados: {self.metricas.frutos_cosechados}")
            print(f"  • Cosechas realizadas: {self.metricas.cosechas_ordenadas}")
            print(f"  • Tratamientos aplicados: {self.metricas.tratamientos_ordenados}")
            print(f"  • Celdas críticas detectadas: {self.metricas.celdas_criticas}")
            print(f"  • Celdas de alto riesgo: {self.metricas.celdas_alto_riesgo}")
            print(f"  • Agentes utilizados: {self.metricas.agentes_activos}")
            
            # Eficiencia
            if self.metricas.tiempo_transcurrido > 0:
                celdas_por_minuto = (self.metricas.celdas_exploradas / self.metricas.tiempo_transcurrido) * 60
                frutos_por_minuto = (self.metricas.frutos_cosechados / self.metricas.tiempo_transcurrido) * 60
                print(f"\n⚡ EFICIENCIA:")
                print(f"  • {celdas_por_minuto:.1f} celdas/minuto")
                print(f"  • {frutos_por_minuto:.1f} frutos cosechados/minuto")
            
            # Estadísticas de eventos
            total_eventos = len(self.registro.eventos)
            eventos_cosecha = sum(1 for e in self.registro.eventos if e['tipo'] == 'cosecha')
            eventos_tratamiento = sum(1 for e in self.registro.eventos if e['tipo'] == 'tratamiento')
            eventos_alerta = sum(1 for e in self.registro.eventos if e['tipo'] == 'alerta')
            
            print(f"\n📋 EVENTOS REGISTRADOS:")
            print(f"  • Total: {total_eventos}")
            print(f"  • Cosechas detectadas: {eventos_cosecha}")
            print(f"  • Tratamientos necesarios: {eventos_tratamiento}")
            print(f"  • Alertas críticas: {eventos_alerta}")
        
        print("\n" + "="*90 + "\n")