# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
AGENTE UI - VISUALIZACION PYGAME + RESUMEN TERMINAL
====================================================

Responsabilidades:
1. Visualizar simulacion en tiempo real con Pygame
2. Mostrar grid del cultivo con colores
3. Mostrar agentes moviendose
4. MOSTRAR AL CAPATAZ como figura fija
5. Mostrar metricas en pantalla
6. Generar resumen final en terminal
=======
UI VISUAL
=========
Dibuja el Capataz (figura geométrica), el Grid, los Agentes y sus Órdenes.
>>>>>>> Simulation
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

<<<<<<< HEAD

# CONFIGURACION DE PYGAME

class ConfigPygame:
    """Configuracion visual de Pygame"""
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
    
    # Colores de agentes
    COLORES_AGENTES = [
        (33, 150, 243),   # Azul
        (76, 175, 80),    # Verde
        (255, 152, 0),    # Naranja
        (233, 30, 99),    # Rosa
        (0, 188, 212),    # Cyan
    ]
    
    # Color del capataz
    COLOR_CAPATAZ = (139, 69, 19)  # Marron
    COLOR_CAPATAZ_BORDE = (255, 215, 0)  # Dorado
    
    # Fuentes
    FONT_SIZE_TITLE = 28
    FONT_SIZE_SUBTITLE = 20
    FONT_SIZE_NORMAL = 16
    FONT_SIZE_SMALL = 14
    
    # Animacion
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


# AGENTE UI CON PYGAME Y CAPATAZ

class AgenteUI:
    """
    Agente UI: Visualizacion con Pygame + Resumen en Terminal
    COMPATIBLE CON macOS - Ejecuta Pygame en el thread principal
    
    Caracteristicas:
    - Visualizacion en tiempo real del grid
    - Agentes moviendose por el cultivo
    - CAPATAZ visible como figura fija supervisando
    - Codigo de colores para riesgos
    - Panel de metricas en vivo
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
        
        # NUEVO: Posicion del capataz
        self.posicion_capataz = (0, 0)
        
        # Registro de actividad
        self.registro = RegistroActividad(max_eventos=1000)
        
        # Control
        self.running = True
        self.pygame_iniciado = False
        
        # Referencias de Pygame
=======
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
        
>>>>>>> Simulation
        self.screen = None
        self.running = True
        
<<<<<<< HEAD
        print(f"[UI] [OK] Agente UI inicializado - Grid: {grid_filas}x{grid_columnas}")
    
    # ========================================================================
    # INICIALIZACION DE PYGAME (THREAD PRINCIPAL)
    # ========================================================================
    
=======
        # Datos a renderizar
        self.celdas = []
        self.agentes = []
        self.metricas = None

>>>>>>> Simulation
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
<<<<<<< HEAD
            self.clock.tick(ConfigPygame.FPS)
    
    def actualizar_frame(self):
        """Actualiza un solo frame (útil para control manual del loop)"""
        if not self.pygame_iniciado:
            return
=======
            self.clock.tick(30)
>>>>>>> Simulation
        
        pygame.quit()

    def _dibujar_capataz(self):
        """Dibuja la figura geométrica fija que representa al Capataz"""
        cx, cy = self.width // 2, 50
        # Triángulo (El Ojo)
        puntos = [(cx, cy - 30), (cx - 30, cy + 20), (cx + 30, cy + 20)]
        pygame.draw.polygon(self.screen, COLOR_CAPATAZ, puntos)
        pygame.draw.circle(self.screen, (0,0,0), (cx, cy), 10) # Pupila
        
<<<<<<< HEAD
        # Renderizar
        self._renderizar_pygame()
        
        # Actualizar pantalla
        pygame.display.flip()
        self.clock.tick(ConfigPygame.FPS)
    
    # ========================================================================
    # RENDERIZADO PYGAME
    # ========================================================================
    
    def _renderizar_pygame(self):
        """Renderiza toda la visualizacion en Pygame"""
        if not self.screen:
            return
        
        # Fondo
        self.screen.fill(ConfigPygame.COLOR_BG)
        
        # Header
        self._dibujar_header()
        
        # Grid del cultivo
        self._dibujar_grid()
        
        # CAPATAZ (dibujarlo antes de los agentes para que este al fondo)
        self._dibujar_capataz()
        
        # Agentes
        self._dibujar_agentes()
        
        # Panel de informacion
        self._dibujar_panel_info()
        
        # Footer
        self._dibujar_footer()
    
    def _dibujar_header(self):
        """Dibuja el encabezado"""
        y_offset = 10
        
        # Titulo
        titulo = self.font_title.render("SISTEMA MULTI-AGENTE - MONITOREO DE CULTIVO", True, ConfigPygame.COLOR_TEXT)
        titulo_rect = titulo.get_rect(center=(self.window_width // 2, y_offset + 20))
        self.screen.blit(titulo, titulo_rect)
        
        # Tiempo y progreso
        if self.metricas:
            mins = int(self.metricas.tiempo_transcurrido // 60)
            segs = int(self.metricas.tiempo_transcurrido % 60)
            
            info = self.font_normal.render(
                f"Tiempo: {mins:02d}:{segs:02d}  |  Progreso: {self.metricas.porcentaje_analizado:.1f}%  |  [CAPATAZ] Capataz supervisando",
                True, ConfigPygame.COLOR_TEXT_DIM
            )
            info_rect = info.get_rect(center=(self.window_width // 2, y_offset + 50))
            self.screen.blit(info, info_rect)
        
        # Linea separadora
        pygame.draw.line(
            self.screen,
            ConfigPygame.COLOR_GRID,
            (0, ConfigPygame.HEADER_HEIGHT - 5),
            (self.window_width, ConfigPygame.HEADER_HEIGHT - 5),
            2
        )
    
=======
        # Texto del Capataz
        txt = self.font_big.render("EL CAPATAZ", True, COLOR_CAPATAZ)
        self.screen.blit(txt, (cx - 50, cy + 25))

>>>>>>> Simulation
    def _dibujar_grid(self):
        start_x = 20
        start_y = MARGIN_TOP
        
<<<<<<< HEAD
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
    
    def _dibujar_capataz(self):
        """
        NUEVO: Dibuja al capataz como una figura fija supervisando el huerto
        """
        x_offset = 20
        y_offset = ConfigPygame.HEADER_HEIGHT + 20
        
        # Posicion del capataz (esquina superior izquierda, dentro del grid)
        capataz_x = x_offset + 30
        capataz_y = y_offset + 30
        
        # Dibujar sombrero del capataz (triangulo)
        puntos_sombrero = [
            (capataz_x, capataz_y + 25),
            (capataz_x + 15, capataz_y),
            (capataz_x + 30, capataz_y + 25)
        ]
        pygame.draw.polygon(self.screen, ConfigPygame.COLOR_CAPATAZ, puntos_sombrero)
        pygame.draw.polygon(self.screen, ConfigPygame.COLOR_CAPATAZ_BORDE, puntos_sombrero, 2)
        
        # Dibujar cabeza del capataz (circulo)
        pygame.draw.circle(self.screen, (255, 200, 150), (capataz_x + 15, capataz_y + 32), 14)
        pygame.draw.circle(self.screen, ConfigPygame.COLOR_CAPATAZ_BORDE, (capataz_x + 15, capataz_y + 32), 14, 2)
        
        # Dibujar binoculares/prismaticos (circulos pequenos)
        pygame.draw.circle(self.screen, (50, 50, 50), (capataz_x + 10, capataz_y + 30), 4)
        pygame.draw.circle(self.screen, (50, 50, 50), (capataz_x + 20, capataz_y + 30), 4)
        
        # Dibujar cuerpo/chaleco del capataz (rectangulo)
        pygame.draw.rect(self.screen, (100, 80, 50), (capataz_x + 8, capataz_y + 45, 14, 20), border_radius=3)
        pygame.draw.rect(self.screen, ConfigPygame.COLOR_CAPATAZ_BORDE, (capataz_x + 8, capataz_y + 45, 14, 20), 2, border_radius=3)
        
        # Etiqueta
        texto_capataz = self.font_small.render("CAPATAZ", True, ConfigPygame.COLOR_CAPATAZ_BORDE)
        texto_rect = texto_capataz.get_rect(center=(capataz_x + 15, capataz_y + 75))
        self.screen.blit(texto_capataz, texto_rect)
    
=======
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

>>>>>>> Simulation
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
                
<<<<<<< HEAD
                # Dibujar circulo del agente
                pygame.draw.circle(self.screen, color, (x, y), 15)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 15, 2)
                
                # Dibujar ID del agente
                texto = self.font_small.render(str(agente_id), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(x, y))
                self.screen.blit(texto, texto_rect)
    
    def _dibujar_panel_info(self):
        """Dibuja el panel de informacion lateral"""
        x_offset = self.grid_columnas * ConfigPygame.CELL_SIZE + 40
        y_offset = ConfigPygame.HEADER_HEIGHT + 20
=======
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
>>>>>>> Simulation
        
        if not self.metricas: return
        
<<<<<<< HEAD
        # Titulo del panel
        titulo = self.font_subtitle.render("METRICAS", True, ConfigPygame.COLOR_TEXT)
        self.screen.blit(titulo, (x_offset, y_offset))
        y_offset += 40
        
        # Exploracion
        self._dibujar_seccion_panel(
            "[BUSQUEDA] EXPLORACION",
            [
                f"Celdas: {self.metricas.celdas_exploradas}/{self.metricas.celdas_totales}",
                f"Progreso: {self.metricas.porcentaje_analizado:.1f}%"
            ],
            x_offset, y_offset
        )
        y_offset += 80
        
        # Cosecha
        self._dibujar_seccion_panel(
            "[FRUTOS] COSECHA",
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
            "[ADVERTENCIA] RIESGOS",
            [
                f"Criticos: {self.metricas.celdas_criticas}",
                f"Alto riesgo: {self.metricas.celdas_alto_riesgo}",
                f"Tratamientos: {self.metricas.tratamientos_ordenados}"
            ],
            x_offset, y_offset
        )
        y_offset += 100
        
        # Agentes
        self._dibujar_seccion_panel(
            "[AGENTES] AGENTES",
            [
                f"Total: {self.metricas.agentes_activos}",
                f"Explorando: {self.metricas.agentes_explorando}"
            ],
            x_offset, y_offset
        )
        y_offset += 80
        
        # NUEVO: Info del Capataz
        self._dibujar_seccion_panel(
            "[CAPATAZ] CAPATAZ",
            [
                f"Posicion: {self.posicion_capataz}",
                f"Estado: Supervisando"
            ],
            x_offset, y_offset
        )
        y_offset += 80
        
        # Leyenda de colores
        y_offset += 20
        self._dibujar_leyenda(x_offset, y_offset)
    
    def _dibujar_seccion_panel(self, titulo: str, lineas: List[str], x: int, y: int):
        """Dibuja una seccion del panel de informacion"""
        # Titulo de seccion
        texto_titulo = self.font_normal.render(titulo, True, ConfigPygame.COLOR_TEXT)
        self.screen.blit(texto_titulo, (x, y))
        y += 25
        
        # Lineas de informacion
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
        """Dibuja el pie de pagina"""
        y_offset = self.window_height - ConfigPygame.FOOTER_HEIGHT + 20
        
        # Linea separadora
        pygame.draw.line(
            self.screen,
            ConfigPygame.COLOR_GRID,
            (0, y_offset - 10),
            (self.window_width, y_offset - 10),
            2
        )
        
        # Instrucciones
        texto = self.font_small.render("Presiona ESC para salir  |  [CAPATAZ] Capataz supervisando en esquina superior izquierda", True, ConfigPygame.COLOR_TEXT_DIM)
        texto_rect = texto.get_rect(center=(self.window_width // 2, y_offset + 10))
        self.screen.blit(texto, texto_rect)
    
    # ========================================================================
    # CALLBACK DESDE EL MANAGER
    # ========================================================================
    
    def actualizar(self, estados: List[EstadoCelda], metricas: MetricasSistema):
        """Callback del Manager: recibe actualizaciones del sistema"""
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
                    f"CRITICO en ({estado.x},{estado.y}): {estado.tipo_amenaza}"
                )
    
    def actualizar_posicion_agente(self, agente_id: int, x: int, y: int):
        """Actualiza la posicion de un agente fisico"""
        self.posiciones_agentes[agente_id] = (x, y)
    
    def detener(self):
        """Detiene la visualizacion"""
        self.running = False
        if self.pygame_iniciado:
            pygame.quit()
    
    # ========================================================================
    # RESUMEN FINAL EN TERMINAL
    # ========================================================================
    
    def mostrar_resumen_final(self):
        """Muestra un resumen final en la terminal"""
        # Detener Pygame
        self.detener()
        time.sleep(0.5)
        
        # Limpiar terminal
        os.system('clear' if os.name != 'nt' else 'cls')
        
        print("\n" + "="*90)
        print("[OK] EXPLORACION COMPLETADA - RESUMEN FINAL".center(90))
        print("="*90 + "\n")
        
        if self.metricas:
            mins = int(self.metricas.tiempo_transcurrido // 60)
            segs = int(self.metricas.tiempo_transcurrido % 60)
            
            print(f"⏱  Tiempo total: {mins:02d}:{segs:02d}\n")
            
            print("[DATOS] RESULTADOS:")
            print(f"  • Celdas exploradas: {self.metricas.celdas_exploradas}/{self.metricas.celdas_totales}")
            print(f"  • Cobertura: {self.metricas.porcentaje_analizado:.1f}%")
            print(f"  • Frutos totales detectados: {self.metricas.frutos_totales_detectados}")
            print(f"  • Frutos listos para cosecha: {self.metricas.frutos_listos_cosecha}")
            print(f"  • [FRUTOS] Frutos cosechados: {self.metricas.frutos_cosechados}")
            print(f"  • Cosechas realizadas: {self.metricas.cosechas_ordenadas}")
            print(f"  • Tratamientos aplicados: {self.metricas.tratamientos_ordenados}")
            print(f"  • Celdas criticas detectadas: {self.metricas.celdas_criticas}")
            print(f"  • Celdas de alto riesgo: {self.metricas.celdas_alto_riesgo}")
            print(f"  • Agentes utilizados: {self.metricas.agentes_activos}")
            print(f"  • [CAPATAZ] Capataz: Superviso desde {self.posicion_capataz}")
            
            # Eficiencia
            if self.metricas.tiempo_transcurrido > 0:
                celdas_por_minuto = (self.metricas.celdas_exploradas / self.metricas.tiempo_transcurrido) * 60
                frutos_por_minuto = (self.metricas.frutos_cosechados / self.metricas.tiempo_transcurrido) * 60
                print(f"\n⚡ EFICIENCIA:")
                print(f"  • {celdas_por_minuto:.1f} celdas/minuto")
                print(f"  • {frutos_por_minuto:.1f} frutos cosechados/minuto")
            
            # Estadisticas de eventos
            total_eventos = len(self.registro.eventos)
            eventos_cosecha = sum(1 for e in self.registro.eventos if e['tipo'] == 'cosecha')
            eventos_tratamiento = sum(1 for e in self.registro.eventos if e['tipo'] == 'tratamiento')
            eventos_alerta = sum(1 for e in self.registro.eventos if e['tipo'] == 'alerta')
            
            print(f"\n[INFO] EVENTOS REGISTRADOS:")
            print(f"  • Total: {total_eventos}")
            print(f"  • Cosechas detectadas: {eventos_cosecha}")
            print(f"  • Tratamientos necesarios: {eventos_tratamiento}")
            print(f"  • Alertas criticas: {eventos_alerta}")
        
        print("\n" + "="*90 + "\n")
=======
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
>>>>>>> Simulation
