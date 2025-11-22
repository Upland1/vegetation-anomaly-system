"""
AGENTE MANAGER - LÓGICA CENTRAL DE DECISIÓN
=============================================

Responsabilidades:
1. Recibir datos de riesgo de los agentes exploradores
2. Evaluar riesgos con umbrales y reglas
3. Establecer prioridades y protocolo de acción
4. Enviar instrucciones formales al Agente Físico
5. Enviar información de estado al Agente UI

NO hace:
- Movimiento de agentes (lo hace Agente Físico)
- Exploración directa (lo hace Agente Físico)
- Visualización (lo hace Agente UI)
"""

from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

# ============================================================================
# ESTRUCTURAS DE DATOS COMPARTIDAS (IMPORTAR DESDE AQUÍ)
# ============================================================================

class NivelRiesgo(Enum):
    """Niveles de riesgo para el análisis"""
    SIN_DATOS = 0
    BAJO = 1
    MEDIO = 2
    ALTO = 3
    CRITICO = 4


class TipoAmenaza(Enum):
    """Tipos de amenazas detectables"""
    PLAGA = "Plaga"
    HONGO = "Hongo"
    SEQUIA = "Sequía"
    EXCESO_AGUA = "Exceso de agua"
    NUTRIENTES_BAJOS = "Nutrientes bajos"
    TEMPERATURA_ALTA = "Temperatura alta"
    TEMPERATURA_BAJA = "Temperatura baja"


@dataclass
class DatosExploracion:
    """
    Datos que envía el Agente Físico al Manager después de explorar
    
    AGENTE FÍSICO: Envía esto después de capturar datos en una celda
    """
    x: int
    y: int
    temperatura: float
    humedad: float
    nivel_plagas: float
    nivel_nutrientes: float
    timestamp: datetime = field(default_factory=datetime.now)
    agente_id: int = 0


@dataclass
class InstruccionTratamiento:
    """
    Instrucción que el Manager envía al Agente Físico
    
    AGENTE FÍSICO: Recibe esto para ejecutar un tratamiento
    """
    celda_objetivo: Tuple[int, int]
    tipo_tratamiento: str  # "aplicar_pesticida", "riego", "fertilizacion", etc.
    nivel_urgencia: int  # 1-5, siendo 5 la más urgente
    tipo_amenaza: str
    descripcion: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"Tratamiento en {self.celda_objetivo}: {self.tipo_tratamiento} (Urgencia: {self.nivel_urgencia})"


@dataclass
class EstadoCelda:
    """
    Estado procesado de una celda para enviar a la UI
    
    AGENTE UI: Recibe esto para visualizar el mapa
    """
    x: int
    y: int
    nivel_riesgo: NivelRiesgo
    tipo_amenaza: str
    valor_riesgo: float
    requiere_tratamiento: bool
    prioridad: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricasSistema:
    """
    Métricas del sistema para la UI
    
    AGENTE UI: Recibe esto para mostrar estadísticas
    """
    tiempo_transcurrido: float = 0.0
    celdas_exploradas: int = 0
    celdas_totales: int = 0
    porcentaje_analizado: float = 0.0
    celdas_criticas: int = 0
    celdas_alto_riesgo: int = 0
    tratamientos_ordenados: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# AGENTE MANAGER
# ============================================================================

class AgenteManager:
    """
    Agente Manager: Núcleo de decisión del sistema
    
    FLUJO:
    1. Agente Físico explora → envía DatosExploracion
    2. Manager evalúa riesgos → determina si necesita tratamiento
    3. Si necesita tratamiento → envía InstruccionTratamiento al Agente Físico
    4. Siempre → envía EstadoCelda y MetricasSistema a UI
    """
    
    def __init__(self, grid_filas: int = 10, grid_columnas: int = 10):
        """
        Inicializa el Agente Manager
        
        Args:
            grid_filas: Número de filas del cultivo
            grid_columnas: Número de columnas del cultivo
        """
        # Configuración del grid
        self.grid_filas = grid_filas
        self.grid_columnas = grid_columnas
        self.celdas_totales = grid_filas * grid_columnas
        
        # Almacenamiento de datos
        self.mapa_estados: Dict[Tuple[int, int], EstadoCelda] = {}
        self.datos_crudos: Dict[Tuple[int, int], DatosExploracion] = {}
        self.tratamientos_pendientes: List[InstruccionTratamiento] = []
        
        # Control de exploración
        self.celdas_exploradas: set = set()
        
        # Métricas
        self.tiempo_inicio = time.time()
        self.tratamientos_ordenados_total = 0
        
        # Callbacks para comunicación con otros agentes
        self._callback_agente_fisico: Optional[Callable] = None
        self._callback_agente_ui: Optional[Callable] = None
        
        # Umbrales de riesgo (configurables)
        self.umbrales = {
            'temperatura_min': 15.0,
            'temperatura_max': 30.0,
            'humedad_min': 40.0,
            'humedad_max': 80.0,
            'nivel_plagas_critico': 7.0,
            'nivel_plagas_alto': 5.0,
            'nivel_nutrientes_bajo': 4.0,
        }
        
        print(f"[Manager] Inicializado - Grid: {grid_filas}x{grid_columnas}")
    
    # ========================================================================
    # CONFIGURACIÓN
    # ========================================================================
    
    def registrar_agente_fisico(self, callback: Callable[[InstruccionTratamiento], None]):
        """
        Registra el callback para comunicarse con el Agente Físico
        
        Args:
            callback: Función que recibe InstruccionTratamiento
            
        Ejemplo:
            def recibir_instruccion(instruccion: InstruccionTratamiento):
                print(f"Ejecutando: {instruccion}")
            
            manager.registrar_agente_fisico(recibir_instruccion)
        """
        self._callback_agente_fisico = callback
        print("[Manager] Agente Físico registrado")
    
    def registrar_agente_ui(self, callback: Callable[[List[EstadoCelda], MetricasSistema], None]):
        """
        Registra el callback para comunicarse con el Agente UI
        
        Args:
            callback: Función que recibe (estados, metricas)
            
        Ejemplo:
            def actualizar_visualizacion(estados: List[EstadoCelda], metricas: MetricasSistema):
                for estado in estados:
                    ui.pintar_celda(estado.x, estado.y, estado.nivel_riesgo)
                ui.actualizar_panel(metricas)
            
            manager.registrar_agente_ui(actualizar_visualizacion)
        """
        self._callback_agente_ui = callback
        print("[Manager] Agente UI registrado")
    
    def configurar_umbrales(self, nuevos_umbrales: Dict[str, float]):
        """
        Configura o actualiza los umbrales de riesgo
        
        Args:
            nuevos_umbrales: Diccionario con umbrales a actualizar
        """
        self.umbrales.update(nuevos_umbrales)
        print(f"[Manager] Umbrales actualizados")
    
    # ========================================================================
    # RECEPCIÓN DE DATOS (DESDE AGENTE FÍSICO)
    # ========================================================================
    
    def recibir_datos_exploracion(self, datos: DatosExploracion):
        """
        MÉTODO PRINCIPAL: Recibe datos del Agente Físico
        
        El Agente Físico llama este método después de explorar una celda
        
        Args:
            datos: DatosExploracion con info de sensores
            
        Proceso:
        1. Almacena datos crudos
        2. Evalúa riesgo
        3. Determina si necesita tratamiento
        4. Si necesita → envía instrucción a Agente Físico
        5. Actualiza UI con nuevo estado
        """
        pos = (datos.x, datos.y)
        
        # Almacenar datos crudos
        self.datos_crudos[pos] = datos
        self.celdas_exploradas.add(pos)
        
        # EVALUAR RIESGO (Lógica central de decisión)
        estado_celda = self._evaluar_riesgo(datos)
        self.mapa_estados[pos] = estado_celda
        
        print(f"[Manager] Celda ({datos.x}, {datos.y}) evaluada - Riesgo: {estado_celda.nivel_riesgo.name}")
        
        # Si requiere tratamiento → generar instrucción
        if estado_celda.requiere_tratamiento:
            instruccion = self._generar_instruccion_tratamiento(estado_celda)
            self.tratamientos_pendientes.append(instruccion)
            self.tratamientos_ordenados_total += 1
            
            # ENVIAR A AGENTE FÍSICO
            if self._callback_agente_fisico:
                self._callback_agente_fisico(instruccion)
            
            print(f"[Manager] ⚠️  Instrucción enviada a Agente Físico: {instruccion}")
        
        # ENVIAR A UI (siempre)
        self._notificar_ui()
    
    # ========================================================================
    # LÓGICA DE EVALUACIÓN DE RIESGOS
    # ========================================================================
    
    def _evaluar_riesgo(self, datos: DatosExploracion) -> EstadoCelda:
        """
        Evalúa el nivel de riesgo basado en datos de sensores
        Aplica umbrales y reglas para determinar amenazas
        
        Returns:
            EstadoCelda con la evaluación completa
        """
        riesgos_detectados = []
        
        # REGLA 1: Evaluar temperatura
        if datos.temperatura < self.umbrales['temperatura_min']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.TEMPERATURA_BAJA,
                'valor': abs(datos.temperatura - self.umbrales['temperatura_min']),
                'descripcion': f"Temperatura baja ({datos.temperatura:.1f}°C)"
            })
        elif datos.temperatura > self.umbrales['temperatura_max']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.TEMPERATURA_ALTA,
                'valor': abs(datos.temperatura - self.umbrales['temperatura_max']),
                'descripcion': f"Temperatura alta ({datos.temperatura:.1f}°C)"
            })
        
        # REGLA 2: Evaluar humedad
        if datos.humedad < self.umbrales['humedad_min']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.SEQUIA,
                'valor': abs(datos.humedad - self.umbrales['humedad_min']),
                'descripcion': f"Humedad baja ({datos.humedad:.1f}%)"
            })
        elif datos.humedad > self.umbrales['humedad_max']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.EXCESO_AGUA,
                'valor': abs(datos.humedad - self.umbrales['humedad_max']),
                'descripcion': f"Humedad alta ({datos.humedad:.1f}%)"
            })
        
        # REGLA 3: Evaluar plagas (CRÍTICO)
        if datos.nivel_plagas >= self.umbrales['nivel_plagas_critico']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.PLAGA,
                'valor': datos.nivel_plagas,
                'descripcion': f"Plaga crítica (nivel {datos.nivel_plagas:.1f})"
            })
        elif datos.nivel_plagas >= self.umbrales['nivel_plagas_alto']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.PLAGA,
                'valor': datos.nivel_plagas,
                'descripcion': f"Plaga detectada (nivel {datos.nivel_plagas:.1f})"
            })
        
        # REGLA 4: Evaluar nutrientes
        if datos.nivel_nutrientes < self.umbrales['nivel_nutrientes_bajo']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.NUTRIENTES_BAJOS,
                'valor': abs(datos.nivel_nutrientes - self.umbrales['nivel_nutrientes_bajo']),
                'descripcion': f"Nutrientes bajos (nivel {datos.nivel_nutrientes:.1f})"
            })
        
        # Si no hay riesgos → estado normal
        if not riesgos_detectados:
            return EstadoCelda(
                x=datos.x,
                y=datos.y,
                nivel_riesgo=NivelRiesgo.BAJO,
                tipo_amenaza="Normal",
                valor_riesgo=0.0,
                requiere_tratamiento=False,
                prioridad=1
            )
        
        # Seleccionar el riesgo más crítico
        riesgo_principal = max(riesgos_detectados, key=lambda r: r['valor'])
        
        # ESTABLECER PRIORIDADES Y PROTOCOLO
        nivel, prioridad, requiere = self._calcular_nivel_y_prioridad(
            riesgo_principal['valor'], 
            riesgo_principal['tipo']
        )
        
        return EstadoCelda(
            x=datos.x,
            y=datos.y,
            nivel_riesgo=nivel,
            tipo_amenaza=riesgo_principal['tipo'].value,
            valor_riesgo=riesgo_principal['valor'],
            requiere_tratamiento=requiere,
            prioridad=prioridad
        )
    
    def _calcular_nivel_y_prioridad(self, valor: float, amenaza: TipoAmenaza) -> Tuple[NivelRiesgo, int, bool]:
        """
        Determina nivel de riesgo, prioridad y si requiere tratamiento
        
        Returns:
            (NivelRiesgo, prioridad 1-5, requiere_tratamiento)
        """
        # Lógica especial para plagas (más crítico)
        if amenaza == TipoAmenaza.PLAGA:
            if valor >= 9.0:
                return (NivelRiesgo.CRITICO, 5, True)
            elif valor >= 7.0:
                return (NivelRiesgo.ALTO, 4, True)
            elif valor >= 5.0:
                return (NivelRiesgo.MEDIO, 3, True)
            else:
                return (NivelRiesgo.BAJO, 2, False)
        
        # Lógica para otras amenazas
        if valor >= 15.0:
            return (NivelRiesgo.CRITICO, 5, True)
        elif valor >= 10.0:
            return (NivelRiesgo.ALTO, 4, True)
        elif valor >= 5.0:
            return (NivelRiesgo.MEDIO, 3, False)
        else:
            return (NivelRiesgo.BAJO, 2, False)
    
    # ========================================================================
    # GENERACIÓN DE INSTRUCCIONES (PARA AGENTE FÍSICO)
    # ========================================================================
    
    def _generar_instruccion_tratamiento(self, estado: EstadoCelda) -> InstruccionTratamiento:
        """
        Genera la instrucción formal de tratamiento para el Agente Físico
        
        PROTOCOLO DE ACCIÓN según tipo de amenaza
        """
        # Mapeo de amenaza → tratamiento
        protocolos = {
            TipoAmenaza.PLAGA.value: {
                'tratamiento': 'aplicar_pesticida',
                'descripcion': 'Aplicar pesticida orgánico en área afectada'
            },
            TipoAmenaza.HONGO.value: {
                'tratamiento': 'aplicar_fungicida',
                'descripcion': 'Aplicar fungicida y mejorar ventilación'
            },
            TipoAmenaza.SEQUIA.value: {
                'tratamiento': 'riego_intensivo',
                'descripcion': 'Incrementar frecuencia de riego'
            },
            TipoAmenaza.EXCESO_AGUA.value: {
                'tratamiento': 'mejorar_drenaje',
                'descripcion': 'Reducir riego y mejorar drenaje'
            },
            TipoAmenaza.NUTRIENTES_BAJOS.value: {
                'tratamiento': 'aplicar_fertilizante',
                'descripcion': 'Aplicar fertilizante balanceado'
            },
            TipoAmenaza.TEMPERATURA_ALTA.value: {
                'tratamiento': 'activar_ventilacion',
                'descripcion': 'Activar ventilación y sombreado'
            },
            TipoAmenaza.TEMPERATURA_BAJA.value: {
                'tratamiento': 'activar_calefaccion',
                'descripcion': 'Activar calefacción del invernadero'
            }
        }
        
        protocolo = protocolos.get(estado.tipo_amenaza, {
            'tratamiento': 'inspeccion_manual',
            'descripcion': 'Requiere inspección manual'
        })
        
        return InstruccionTratamiento(
            celda_objetivo=(estado.x, estado.y),
            tipo_tratamiento=protocolo['tratamiento'],
            nivel_urgencia=estado.prioridad,
            tipo_amenaza=estado.tipo_amenaza,
            descripcion=protocolo['descripcion']
        )
    
    # ========================================================================
    # COMUNICACIÓN CON UI
    # ========================================================================
    
    def _notificar_ui(self):
        """Envía actualización al Agente UI"""
        if not self._callback_agente_ui:
            return
        
        # Preparar lista de estados
        estados = list(self.mapa_estados.values())
        
        # Calcular métricas
        metricas = self._calcular_metricas()
        
        # ENVIAR A UI
        self._callback_agente_ui(estados, metricas)
    
    def _calcular_metricas(self) -> MetricasSistema:
        """Calcula métricas actuales del sistema"""
        celdas_criticas = sum(
            1 for e in self.mapa_estados.values() 
            if e.nivel_riesgo == NivelRiesgo.CRITICO
        )
        
        celdas_alto = sum(
            1 for e in self.mapa_estados.values() 
            if e.nivel_riesgo == NivelRiesgo.ALTO
        )
        
        return MetricasSistema(
            tiempo_transcurrido=time.time() - self.tiempo_inicio,
            celdas_exploradas=len(self.celdas_exploradas),
            celdas_totales=self.celdas_totales,
            porcentaje_analizado=(len(self.celdas_exploradas) / self.celdas_totales) * 100,
            celdas_criticas=celdas_criticas,
            celdas_alto_riesgo=celdas_alto,
            tratamientos_ordenados=self.tratamientos_ordenados_total
        )
    
    # ========================================================================
    # CONSULTAS PÚBLICAS
    # ========================================================================
    
    def obtener_estado_completo(self) -> Dict:
        """
        Retorna el estado completo del sistema
        Útil para debugging o análisis
        """
        return {
            'mapa_estados': self.mapa_estados,
            'metricas': self._calcular_metricas(),
            'tratamientos_pendientes': self.tratamientos_pendientes,
            'exploracion_completa': len(self.celdas_exploradas) == self.celdas_totales
        }
    
    def generar_reporte(self) -> str:
        """Genera reporte textual del estado actual"""
        metricas = self._calcular_metricas()
        
        reporte = f"""
{'='*70}
REPORTE DEL SISTEMA - AGENTE MANAGER
{'='*70}

EXPLORACIÓN:
  • Celdas exploradas: {metricas.celdas_exploradas}/{metricas.celdas_totales}
  • Progreso: {metricas.porcentaje_analizado:.1f}%
  • Tiempo transcurrido: {metricas.tiempo_transcurrido:.1f}s

ANÁLISIS DE RIESGOS:
  • Celdas críticas: {metricas.celdas_criticas}
  • Celdas alto riesgo: {metricas.celdas_alto_riesgo}
  • Tratamientos ordenados: {metricas.tratamientos_ordenados}
  • Tratamientos pendientes: {len(self.tratamientos_pendientes)}

UMBRALES CONFIGURADOS:
"""
        for key, value in self.umbrales.items():
            reporte += f"  • {key}: {value}\n"
        
        reporte += f"{'='*70}\n"
        return reporte


# ============================================================================
# EJEMPLO DE INTEGRACIÓN
# ============================================================================

def ejemplo_uso():
    """
    Ejemplo de cómo integrar el Manager con Agente Físico y UI
    """
    print("\n" + "="*70)
    print("EJEMPLO DE INTEGRACIÓN - AGENTE MANAGER")
    print("="*70 + "\n")
    
    # ========================================================================
    # 1. CREAR MANAGER
    # ========================================================================
    manager = AgenteManager(grid_filas=10, grid_columnas=10)
    
    # ========================================================================
    # 2. AGENTE FÍSICO: Registrar callback
    # ========================================================================
    def agente_fisico_ejecutar(instruccion: InstruccionTratamiento):
        """
        Esta función la implementa el equipo del Agente Físico
        """
        print(f"\n[Agente Físico] 🤖 RECIBIDA: {instruccion}")
        print(f"[Agente Físico] Moviendo a celda {instruccion.celda_objetivo}")
        print(f"[Agente Físico] Ejecutando: {instruccion.descripcion}")
        # Aquí va el código del agente físico para moverse y aplicar tratamiento
    
    manager.registrar_agente_fisico(agente_fisico_ejecutar)
    
    # ========================================================================
    # 3. AGENTE UI: Registrar callback
    # ========================================================================
    def agente_ui_actualizar(estados: List[EstadoCelda], metricas: MetricasSistema):
        """
        Esta función la implementa el equipo de UI
        """
        print(f"\n[Agente UI] 🖥️  Actualizando visualización")
        print(f"[Agente UI] Celdas: {len(estados)} | Progreso: {metricas.porcentaje_analizado:.1f}%")
        # Aquí va el código para actualizar la interfaz gráfica
    
    manager.registrar_agente_ui(agente_ui_actualizar)
    
    # ========================================================================
    # 4. SIMULACIÓN: Agente Físico envía datos al explorar
    # ========================================================================
    print("\n--- SIMULANDO EXPLORACIÓN ---\n")
    
    import random
    
    # Simular que el agente físico explora 5 celdas
    for i in range(5):
        # El agente físico captura datos y los envía al Manager
        datos = DatosExploracion(
            x=random.randint(0, 9),
            y=random.randint(0, 9),
            temperatura=random.uniform(10, 35),
            humedad=random.uniform(30, 90),
            nivel_plagas=random.uniform(0, 10),
            nivel_nutrientes=random.uniform(3, 10),
            agente_id=0
        )
        
        print(f"\n[Agente Físico] Explorando celda ({datos.x}, {datos.y})")
        print(f"[Agente Físico] Datos capturados: T={datos.temperatura:.1f}°C, H={datos.humedad:.1f}%, Plagas={datos.nivel_plagas:.1f}")
        
        # ENVIAR DATOS AL MANAGER
        manager.recibir_datos_exploracion(datos)
        
        time.sleep(0.5)
    
    # ========================================================================
    # 5. REPORTE FINAL
    # ========================================================================
    print("\n" + manager.generar_reporte())


if __name__ == "__main__":
    ejemplo_uso()