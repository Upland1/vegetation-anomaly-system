"""
AGENTE FÍSICO - SISTEMA DE EXPLORACIÓN Y EJECUCIÓN
===================================================

Responsabilidades:
1. Explorar celdas asignadas
2. Capturar datos de sensores
3. Detectar jitomates y su estado
4. Enviar datos al Manager
5. Ejecutar instrucciones (COSECHA y TRATAMIENTO)
6. Reportar resultados
"""

import time
import random
from typing import Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime
import queue
from threading import Lock

# Importar desde el Manager
from manager import (
    DatosExploracion,
    InstruccionCosecha,
    InstruccionTratamiento,
)


# CONFIGURACIÓN DEL AGENTE FÍSICO

@dataclass
class ConfiguracionAgente:
    """Configuración de un agente físico"""
    agente_id: int
    velocidad_movimiento: float = 1.0  # segundos por celda
    velocidad_cosecha: float = 0.5     # segundos por fruto
    velocidad_tratamiento: float = 2.0 # segundos por tratamiento
    capacidad_carga: int = 50          # máximo de frutos que puede cargar
    bateria_inicial: float = 100.0     # porcentaje de batería


# AGENTE FÍSICO

class AgenteFisico:
    """
    Agente Físico: Explora, captura datos y ejecuta instrucciones
    
    FLUJO PRINCIPAL:
    1. Recibe asignación de celdas del Manager
    2. Explora cada celda capturando datos
    3. Envía DatosExploracion al Manager
    4. Ejecuta instrucciones recibidas del Manager
    5. Reporta resultados al Manager
    """
    
    def __init__(
        self, 
        agente_id: int,
        callback_enviar_datos,
        callback_reportar_cosecha,
        config: Optional[ConfiguracionAgente] = None
    ):
        """
        Inicializa el Agente Físico
        
        Args:
            agente_id: ID único del agente (1-5)
            callback_enviar_datos: Función para enviar datos al Manager
            callback_reportar_cosecha: Función para reportar cosechas al Manager
            config: Configuración personalizada
        """
        self.agente_id = agente_id
        self.config = config or ConfiguracionAgente(agente_id=agente_id)
        
        # Callbacks para comunicarse con el Manager
        self.callback_enviar_datos = callback_enviar_datos
        self.callback_reportar_cosecha = callback_reportar_cosecha
        
        # Posición actual
        self.posicion_actual: Tuple[int, int] = (0, 0)
        
        # Estado del agente
        self.bateria = self.config.bateria_inicial
        self.frutos_cargados = 0
        self.cosechas_completadas = 0
        self.tratamientos_completados = 0
        self.celdas_exploradas = 0
        
        # Control de instrucciones
        self.cola_instrucciones = queue.Queue()
        self.procesando_instruccion = False
        self.lock = Lock()
        
        # Flags de control
        self.activo = False
        self.exploracion_completa = False
        
        # Celdas asignadas por el Manager
        self.celdas_asignadas: List[Tuple[int, int]] = []
        
        print(f"[Agente {self.agente_id}] ✅ Inicializado")
        print(f"[Agente {self.agente_id}] Batería: {self.bateria}%")
        print(f"[Agente {self.agente_id}] Capacidad: {self.config.capacidad_carga} frutos")
    
    # ASIGNACIÓN DE TRABAJO (DESDE EL MANAGER)
    
    def asignar_celdas(self, celdas: List[Tuple[int, int]]):
        """
        El Manager llama esto para asignar celdas a explorar
        
        Args:
            celdas: Lista de coordenadas (x, y) a explorar
        """
        self.celdas_asignadas = celdas
        print(f"[Agente {self.agente_id}] 📋 Asignadas {len(celdas)} celdas")
    
    # EXPLORACIÓN
    
    def iniciar_exploracion(self):
        """
        Inicia el proceso de exploración de las celdas asignadas
        
        El Manager llama esto para iniciar el trabajo del agente
        """
        if not self.celdas_asignadas:
            print(f"[Agente {self.agente_id}] ⚠️  Sin celdas asignadas")
            return
        
        self.activo = True
        print(f"\n[Agente {self.agente_id}] 🚀 Iniciando exploración")
        print(f"[Agente {self.agente_id}] Ruta: {len(self.celdas_asignadas)} celdas")
        
        for celda in self.celdas_asignadas:
            if not self.activo:
                break
            
            # Verificar batería
            if self.bateria < 10:
                print(f"[Agente {self.agente_id}] 🔋 Batería baja, recargando...")
                self._recargar_bateria()
            
            # Verificar capacidad de carga
            if self.frutos_cargados >= self.config.capacidad_carga:
                print(f"[Agente {self.agente_id}] 📦 Capacidad llena, descargando...")
                self._descargar_frutos()
            
            # Explorar celda
            self._explorar_celda(celda)
            self.celdas_exploradas += 1
            
            # Procesar instrucciones pendientes
            self._procesar_instrucciones_pendientes()
        
        self.exploracion_completa = True
        print(f"\n[Agente {self.agente_id}] ✅ Exploración completada")
        self._mostrar_estadisticas()
    
    def _explorar_celda(self, celda: Tuple[int, int]):
        """
        Explora una celda específica
        
        Proceso:
        1. Moverse a la celda
        2. Capturar datos de sensores
        3. Analizar estado de frutos
        4. Enviar datos al Manager
        """
        print(f"\n[Agente {self.agente_id}] 📍 Explorando celda {celda}")
        
        # 1. MOVERSE A LA CELDA
        self._mover_a(celda)
        
        # 2. CAPTURAR DATOS DE SENSORES
        datos = self._capturar_datos_sensores(celda)
        
        # 3. MOSTRAR INFORMACIÓN
        print(f"[Agente {self.agente_id}] 🌡️  T={datos.temperatura:.1f}°C | H={datos.humedad:.1f}%")
        print(f"[Agente {self.agente_id}] 🐛 Plagas={datos.nivel_plagas:.1f} | 🌿 Nutrientes={datos.nivel_nutrientes:.1f}")
        print(f"[Agente {self.agente_id}] 🍅 Frutos: {datos.frutos_disponibles} | Maduración: {datos.nivel_maduracion:.1f}/10")
        
        # 4. ENVIAR DATOS AL MANAGER
        self.callback_enviar_datos(datos)
        
        # Consumir batería
        self.bateria -= 1.0
    
    def _capturar_datos_sensores(self, celda: Tuple[int, int]) -> DatosExploracion:
        """
        Simula la captura de datos de sensores en una celda
        
        En la implementación real, aquí leerías los sensores reales:
        - Sensor de temperatura
        - Sensor de humedad
        - Cámara para detección de plagas
        - Sensor de nutrientes del suelo
        - Cámara RGB para análisis de maduración
        """
        x, y = celda
        
        # Simular lecturas de sensores (con variación realista)
        temperatura = random.uniform(18.0, 32.0)
        humedad = random.uniform(30.0, 85.0)
        nivel_plagas = random.uniform(0.0, 10.0)
        nivel_nutrientes = random.uniform(2.0, 9.0)
        
        # Simular análisis de frutos
        # En la implementación real, usarías visión computacional
        tiene_frutos = random.random() > 0.2  # 80% tienen frutos
        
        if tiene_frutos:
            frutos_disponibles = random.randint(5, 20)
            nivel_maduracion = random.uniform(0.0, 10.0)
            tamano_fruto = random.uniform(4.0, 9.0)
            
            # Color según maduración
            if nivel_maduracion >= 8.0:
                color_rgb = (255, random.randint(30, 70), random.randint(30, 70))  # Rojo
            elif nivel_maduracion >= 5.0:
                color_rgb = (random.randint(200, 255), random.randint(100, 180), random.randint(80, 120))  # Naranja
            else:
                color_rgb = (random.randint(80, 150), random.randint(150, 200), random.randint(70, 120))  # Verde
        else:
            frutos_disponibles = 0
            nivel_maduracion = 0.0
            tamano_fruto = 0.0
            color_rgb = (80, 150, 70)
        
        return DatosExploracion(
            x=x, y=y,
            temperatura=temperatura,
            humedad=humedad,
            nivel_plagas=nivel_plagas,
            nivel_nutrientes=nivel_nutrientes,
            nivel_maduracion=nivel_maduracion,
            tamano_fruto=tamano_fruto,
            color_rgb=color_rgb,
            frutos_disponibles=frutos_disponibles,
            agente_id=self.agente_id
        )
    
    def _mover_a(self, celda: Tuple[int, int]):
        """
        Mueve el agente físico a una celda
        
        En la implementación real, aquí controlarías:
        - Motores del robot
        - Sistema de navegación
        - Evitar obstáculos
        """
        if celda == self.posicion_actual:
            return
        
        distancia = abs(celda[0] - self.posicion_actual[0]) + abs(celda[1] - self.posicion_actual[1])
        tiempo_viaje = distancia * self.config.velocidad_movimiento
        
        print(f"[Agente {self.agente_id}] 🚶 Moviendo de {self.posicion_actual} a {celda}")
        time.sleep(tiempo_viaje * 0.1)  # Simulación acelerada
        
        self.posicion_actual = celda
        self.bateria -= 0.5 * distancia
    
    # EJECUCIÓN DE INSTRUCCIONES (DESDE EL MANAGER)
    
    def recibir_instruccion(self, instruccion):
        """
        El Manager llama esto para enviar instrucciones
        
        Args:
            instruccion: InstruccionCosecha o InstruccionTratamiento
        """
        self.cola_instrucciones.put(instruccion)
    
    def _procesar_instrucciones_pendientes(self):
        """Procesa todas las instrucciones pendientes en la cola"""
        while not self.cola_instrucciones.empty():
            try:
                instruccion = self.cola_instrucciones.get_nowait()
                self._ejecutar_instruccion(instruccion)
            except queue.Empty:
                break
    
    def _ejecutar_instruccion(self, instruccion):
        """Ejecuta una instrucción recibida del Manager"""
        with self.lock:
            self.procesando_instruccion = True
        
        try:
            if isinstance(instruccion, InstruccionCosecha):
                self._ejecutar_cosecha(instruccion)
            elif isinstance(instruccion, InstruccionTratamiento):
                self._ejecutar_tratamiento(instruccion)
        finally:
            with self.lock:
                self.procesando_instruccion = False
    
    def _ejecutar_cosecha(self, instruccion: InstruccionCosecha):
        """
        Ejecuta una instrucción de cosecha
        
        Proceso:
        1. Moverse a la celda objetivo
        2. Activar sistema de recolección
        3. Cosechar frutos
        4. Reportar al Manager
        """
        print(f"\n[Agente {self.agente_id}] 🍅 COSECHA INICIADA")
        print(f"[Agente {self.agente_id}] Objetivo: {instruccion.celda_objetivo}")
        print(f"[Agente {self.agente_id}] Frutos a cosechar: {instruccion.frutos_a_cosechar}")
        print(f"[Agente {self.agente_id}] Prioridad: {instruccion.prioridad}/5")
        
        # 1. Moverse a la celda
        self._mover_a(instruccion.celda_objetivo)
        
        # 2. Verificar capacidad
        frutos_a_recoger = min(
            instruccion.frutos_a_cosechar,
            self.config.capacidad_carga - self.frutos_cargados
        )
        
        if frutos_a_recoger < instruccion.frutos_a_cosechar:
            print(f"[Agente {self.agente_id}] ⚠️  Capacidad limitada: solo {frutos_a_recoger} frutos")
        
        # 3. COSECHAR (simular brazo robótico)
        print(f"[Agente {self.agente_id}] 🤖 Activando sistema de recolección...")
        
        for i in range(frutos_a_recoger):
            time.sleep(self.config.velocidad_cosecha * 0.05)  # Simulación acelerada
            self.frutos_cargados += 1
            self.bateria -= 0.3
            
            if (i + 1) % 5 == 0 or i == frutos_a_recoger - 1:
                print(f"[Agente {self.agente_id}] 🍅 Recolectados: {i + 1}/{frutos_a_recoger}")
        
        self.cosechas_completadas += 1
        
        # 4. REPORTAR AL MANAGER
        self.callback_reportar_cosecha(
            instruccion.celda_objetivo,
            frutos_a_recoger
        )
        
        print(f"[Agente {self.agente_id}] ✅ Cosecha completada: {frutos_a_recoger} frutos")
        print(f"[Agente {self.agente_id}] 📦 Carga actual: {self.frutos_cargados}/{self.config.capacidad_carga}")
    
    def _ejecutar_tratamiento(self, instruccion: InstruccionTratamiento):
        """
        Ejecuta una instrucción de tratamiento
        
        Proceso:
        1. Moverse a la celda objetivo
        2. Identificar tipo de tratamiento
        3. Aplicar tratamiento
        4. Verificar aplicación
        """
        print(f"\n[Agente {self.agente_id}] ⚠️  TRATAMIENTO INICIADO")
        print(f"[Agente {self.agente_id}] Objetivo: {instruccion.celda_objetivo}")
        print(f"[Agente {self.agente_id}] Tipo: {instruccion.tipo_tratamiento}")
        print(f"[Agente {self.agente_id}] Urgencia: {instruccion.nivel_urgencia}/5")
        
        # 1. Moverse a la celda
        self._mover_a(instruccion.celda_objetivo)
        
        # 2. APLICAR TRATAMIENTO
        print(f"[Agente {self.agente_id}] 🤖 {instruccion.descripcion}")
        time.sleep(self.config.velocidad_tratamiento * 0.1)  # Simulación acelerada
        
        self.tratamientos_completados += 1
        self.bateria -= 2.0
        
        print(f"[Agente {self.agente_id}] ✅ Tratamiento completado")
    
    # ========================================================================
    # OPERACIONES AUXILIARES
    # ========================================================================
    
    def _descargar_frutos(self):
        """Descarga los frutos recolectados en el punto de acopio"""
        print(f"\n[Agente {self.agente_id}] 📦 Descargando frutos...")
        time.sleep(0.5)
        print(f"[Agente {self.agente_id}] ✅ {self.frutos_cargados} frutos descargados")
        self.frutos_cargados = 0
    
    def _recargar_bateria(self):
        """Recarga la batería del agente"""
        print(f"[Agente {self.agente_id}] 🔌 Recargando batería...")
        time.sleep(0.5)
        self.bateria = self.config.bateria_inicial
        print(f"[Agente {self.agente_id}] ✅ Batería al 100%")
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas del agente"""
        print(f"\n{'='*60}")
        print(f"ESTADÍSTICAS - AGENTE {self.agente_id}")
        print(f"{'='*60}")
        print(f"📍 Celdas exploradas: {self.celdas_exploradas}")
        print(f"🍅 Cosechas completadas: {self.cosechas_completadas}")
        print(f"⚠️  Tratamientos aplicados: {self.tratamientos_completados}")
        print(f"📦 Frutos en carga: {self.frutos_cargados}")
        print(f"🔋 Batería restante: {self.bateria:.1f}%")
        print(f"{'='*60}\n")
    
    def detener(self):
        """Detiene el agente"""
        self.activo = False
        print(f"[Agente {self.agente_id}] 🛑 Detenido")
    
    def obtener_estadisticas(self) -> dict:
        """Retorna estadísticas del agente para el Manager"""
        return {
            'agente_id': self.agente_id,
            'celdas_exploradas': self.celdas_exploradas,
            'cosechas_completadas': self.cosechas_completadas,
            'tratamientos_completados': self.tratamientos_completados,
            'frutos_cargados': self.frutos_cargados,
            'bateria': self.bateria,
            'exploracion_completa': self.exploracion_completa
        }