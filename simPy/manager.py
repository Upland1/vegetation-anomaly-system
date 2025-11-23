"""
AGENTE MANAGER - LÓGICA CENTRAL DE DECISIÓN
=============================================

Responsabilidades:
1. Recibir datos de riesgo de los agentes exploradores
2. Evaluar riesgos con umbrales y reglas
3. Detectar jitomates listos para cosechar
4. Establecer prioridades y protocolo de acción
5. Enviar instrucciones de COSECHA y TRATAMIENTO al Agente Físico
6. Enviar información de estado al Agente UI
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


class EstadoMaduracion(Enum):
    """Estados de maduración de los jitomates"""
    VERDE = "Verde"
    EN_MADURACION = "En maduración"
    MADURO = "Maduro"
    SOBRE_MADURO = "Sobre maduro"


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
    
    # NUEVOS CAMPOS PARA COSECHA
    nivel_maduracion: float  # 0-10: 0=verde, 5=en maduración, 8+=maduro
    tamano_fruto: float      # 0-10: tamaño del jitomate
    color_rgb: Tuple[int, int, int]  # Color RGB del fruto (para análisis)
    frutos_disponibles: int  # Cantidad de jitomates en esta celda
    
    timestamp: datetime = field(default_factory=datetime.now)
    agente_id: int = 0


@dataclass
class InstruccionCosecha:
    """
    Instrucción de COSECHA que el Manager envía al Agente Físico
    
    AGENTE FÍSICO: Recibe esto para cosechar jitomates maduros
    """
    celda_objetivo: Tuple[int, int]
    frutos_a_cosechar: int
    nivel_maduracion: float
    prioridad: int  # 1-5, siendo 5 la más urgente (sobre maduros)
    descripcion: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"Cosecha en {self.celda_objetivo}: {self.frutos_a_cosechar} frutos (Prioridad: {self.prioridad})"


@dataclass
class InstruccionTratamiento:
    """
    Instrucción de TRATAMIENTO que el Manager envía al Agente Físico
    
    AGENTE FÍSICO: Recibe esto para aplicar tratamientos
    """
    celda_objetivo: Tuple[int, int]
    tipo_tratamiento: str
    nivel_urgencia: int  # 1-5
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
    
    # NUEVOS CAMPOS PARA VISUALIZAR COSECHA
    estado_maduracion: EstadoMaduracion
    frutos_disponibles: int
    listo_para_cosechar: bool
    
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
    
    # NUEVAS MÉTRICAS DE COSECHA
    frutos_totales_detectados: int = 0
    frutos_listos_cosecha: int = 0
    cosechas_ordenadas: int = 0
    frutos_cosechados: int = 0  # Actualizado por Agente Físico
    
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# AGENTE MANAGER
# ============================================================================

class AgenteManager:
    """
    Agente Manager: Núcleo de decisión del sistema
    
    FLUJO COMPLETO:
    1. Agente Físico explora → envía DatosExploracion
    2. Manager evalúa:
       a) ¿Hay jitomates maduros? → InstruccionCosecha
       b) ¿Hay problemas? → InstruccionTratamiento
    3. Prioriza: COSECHA primero, luego tratamientos
    4. Envía instrucciones al Agente Físico
    5. Actualiza UI con estado completo
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
        
        # Colas de instrucciones separadas
        self.cola_cosechas: List[InstruccionCosecha] = []
        self.cola_tratamientos: List[InstruccionTratamiento] = []
        
        # Control de exploración
        self.celdas_exploradas: set = set()
        
        # Métricas
        self.tiempo_inicio = time.time()
        self.cosechas_ordenadas_total = 0
        self.tratamientos_ordenados_total = 0
        self.frutos_cosechados_total = 0
        
        # Callbacks para comunicación con otros agentes
        self._callback_agente_fisico: Optional[Callable] = None
        self._callback_agente_ui: Optional[Callable] = None
        
        # Umbrales de riesgo
        self.umbrales = {
            'temperatura_min': 15.0,
            'temperatura_max': 30.0,
            'humedad_min': 40.0,
            'humedad_max': 80.0,
            'nivel_plagas_critico': 7.0,
            'nivel_plagas_alto': 5.0,
            'nivel_nutrientes_bajo': 4.0,
        }
        
        # NUEVOS: Umbrales de cosecha
        self.umbrales_cosecha = {
            'maduracion_minima': 7.0,      # Nivel mínimo para cosechar
            'maduracion_optima': 8.5,      # Nivel óptimo
            'maduracion_sobre': 9.5,       # Sobre maduro (urgente)
            'tamano_minimo': 5.0,          # Tamaño mínimo del fruto
        }
        
        print(f"[Manager] Inicializado - Grid: {grid_filas}x{grid_columnas}")
        print(f"[Manager] Sistema de COSECHA activado")
    
    # ========================================================================
    # CONFIGURACIÓN
    # ========================================================================
    
    def registrar_agente_fisico(self, callback: Callable):
        """
        Registra el callback para comunicarse con el Agente Físico
        
        Args:
            callback: Función que recibe InstruccionCosecha o InstruccionTratamiento
        """
        self._callback_agente_fisico = callback
        print("[Manager] Agente Físico registrado")
    
    def registrar_agente_ui(self, callback: Callable[[List[EstadoCelda], MetricasSistema], None]):
        """Registra el callback para comunicarse con el Agente UI"""
        self._callback_agente_ui = callback
        print("[Manager] Agente UI registrado")
    
    def configurar_umbrales(self, nuevos_umbrales: Dict[str, float]):
        """Configura umbrales de riesgo"""
        self.umbrales.update(nuevos_umbrales)
        print(f"[Manager] Umbrales de riesgo actualizados")
    
    def configurar_umbrales_cosecha(self, nuevos_umbrales: Dict[str, float]):
        """Configura umbrales de cosecha"""
        self.umbrales_cosecha.update(nuevos_umbrales)
        print(f"[Manager] Umbrales de cosecha actualizados")
    
    # ========================================================================
    # RECEPCIÓN DE DATOS (DESDE AGENTE FÍSICO)
    # ========================================================================
    
    def recibir_datos_exploracion(self, datos: DatosExploracion):
        """
        MÉTODO PRINCIPAL: Recibe datos del Agente Físico
        
        Proceso:
        1. Almacena datos
        2. Evalúa COSECHA (¿hay frutos maduros?)
        3. Evalúa RIESGOS (¿hay problemas?)
        4. Genera instrucciones según prioridad
        5. Actualiza UI
        """
        pos = (datos.x, datos.y)
        
        # Almacenar datos crudos
        self.datos_crudos[pos] = datos
        self.celdas_exploradas.add(pos)
        
        # 1. EVALUAR COSECHA (prioridad)
        if self._requiere_cosecha(datos):
            instruccion_cosecha = self._generar_instruccion_cosecha(datos)
            self.cola_cosechas.append(instruccion_cosecha)
            self.cosechas_ordenadas_total += 1
            
            # ENVIAR INSTRUCCIÓN DE COSECHA
            if self._callback_agente_fisico:
                self._callback_agente_fisico(instruccion_cosecha)
            
            print(f"[Manager] 🍅 COSECHA ordenada: {instruccion_cosecha}")
        
        # 2. EVALUAR RIESGOS
        estado_celda = self._evaluar_riesgo(datos)
        self.mapa_estados[pos] = estado_celda
        
        print(f"[Manager] Celda ({datos.x}, {datos.y}) - Riesgo: {estado_celda.nivel_riesgo.name} | Maduración: {estado_celda.estado_maduracion.name}")
        
        # 3. SI HAY PROBLEMAS → generar tratamiento
        if estado_celda.requiere_tratamiento:
            instruccion_tratamiento = self._generar_instruccion_tratamiento(estado_celda)
            self.cola_tratamientos.append(instruccion_tratamiento)
            self.tratamientos_ordenados_total += 1
            
            # ENVIAR INSTRUCCIÓN DE TRATAMIENTO
            if self._callback_agente_fisico:
                self._callback_agente_fisico(instruccion_tratamiento)
            
            print(f"[Manager] ⚠️  TRATAMIENTO ordenado: {instruccion_tratamiento}")
        
        # 4. ACTUALIZAR UI
        self._notificar_ui()
    
    def reportar_cosecha_completada(self, celda: Tuple[int, int], frutos_cosechados: int):
        """
        El Agente Físico llama esto después de completar una cosecha
        
        Args:
            celda: Posición donde se cosechó
            frutos_cosechados: Cantidad de frutos recolectados
        """
        self.frutos_cosechados_total += frutos_cosechados
        print(f"[Manager] ✅ Cosecha completada en {celda}: {frutos_cosechados} frutos")
        print(f"[Manager] Total cosechado: {self.frutos_cosechados_total} frutos")
        
        # Actualizar UI con nuevas métricas
        self._notificar_ui()
    
    # ========================================================================
    # LÓGICA DE COSECHA
    # ========================================================================
    
    def _requiere_cosecha(self, datos: DatosExploracion) -> bool:
        """
        Determina si una celda tiene jitomates listos para cosechar
        
        Criterios:
        - Nivel de maduración >= umbral mínimo
        - Tamaño del fruto >= tamaño mínimo
        - Hay frutos disponibles
        """
        return (
            datos.frutos_disponibles > 0 and
            datos.nivel_maduracion >= self.umbrales_cosecha['maduracion_minima'] and
            datos.tamano_fruto >= self.umbrales_cosecha['tamano_minimo']
        )
    
    def _generar_instruccion_cosecha(self, datos: DatosExploracion) -> InstruccionCosecha:
        """
        Genera instrucción de cosecha para el Agente Físico
        
        PRIORIZACIÓN:
        - Sobre maduros (>9.5): Prioridad 5 (URGENTE - se pueden echar a perder)
        - Maduros óptimos (8.5-9.5): Prioridad 4
        - Maduros (7.0-8.5): Prioridad 3
        """
        maduracion = datos.nivel_maduracion
        
        if maduracion >= self.umbrales_cosecha['maduracion_sobre']:
            # SOBRE MADUROS - ¡Urgente!
            prioridad = 5
            descripcion = "URGENTE: Frutos sobre maduros, cosechar inmediatamente"
        elif maduracion >= self.umbrales_cosecha['maduracion_optima']:
            # ÓPTIMOS
            prioridad = 4
            descripcion = "Frutos en punto óptimo de maduración"
        else:
            # MADUROS
            prioridad = 3
            descripcion = "Frutos maduros, listos para cosechar"
        
        return InstruccionCosecha(
            celda_objetivo=(datos.x, datos.y),
            frutos_a_cosechar=datos.frutos_disponibles,
            nivel_maduracion=maduracion,
            prioridad=prioridad,
            descripcion=descripcion
        )
    
    def _determinar_estado_maduracion(self, nivel: float) -> EstadoMaduracion:
        """Determina el estado de maduración según el nivel"""
        if nivel >= self.umbrales_cosecha['maduracion_sobre']:
            return EstadoMaduracion.SOBRE_MADURO
        elif nivel >= self.umbrales_cosecha['maduracion_minima']:
            return EstadoMaduracion.MADURO
        elif nivel >= 4.0:
            return EstadoMaduracion.EN_MADURACION
        else:
            return EstadoMaduracion.VERDE
    
    # ========================================================================
    # LÓGICA DE EVALUACIÓN DE RIESGOS
    # ========================================================================
    
    def _evaluar_riesgo(self, datos: DatosExploracion) -> EstadoCelda:
        """
        Evalúa el nivel de riesgo basado en datos de sensores
        """
        riesgos_detectados = []
        
        # REGLA 1: Evaluar temperatura
        if datos.temperatura < self.umbrales['temperatura_min']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.TEMPERATURA_BAJA,
                'valor': abs(datos.temperatura - self.umbrales['temperatura_min']),
            })
        elif datos.temperatura > self.umbrales['temperatura_max']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.TEMPERATURA_ALTA,
                'valor': abs(datos.temperatura - self.umbrales['temperatura_max']),
            })
        
        # REGLA 2: Evaluar humedad
        if datos.humedad < self.umbrales['humedad_min']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.SEQUIA,
                'valor': abs(datos.humedad - self.umbrales['humedad_min']),
            })
        elif datos.humedad > self.umbrales['humedad_max']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.EXCESO_AGUA,
                'valor': abs(datos.humedad - self.umbrales['humedad_max']),
            })
        
        # REGLA 3: Evaluar plagas
        if datos.nivel_plagas >= self.umbrales['nivel_plagas_critico']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.PLAGA,
                'valor': datos.nivel_plagas,
            })
        elif datos.nivel_plagas >= self.umbrales['nivel_plagas_alto']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.PLAGA,
                'valor': datos.nivel_plagas,
            })
        
        # REGLA 4: Evaluar nutrientes
        if datos.nivel_nutrientes < self.umbrales['nivel_nutrientes_bajo']:
            riesgos_detectados.append({
                'tipo': TipoAmenaza.NUTRIENTES_BAJOS,
                'valor': abs(datos.nivel_nutrientes - self.umbrales['nivel_nutrientes_bajo']),
            })
        
        # Determinar estado de maduración
        estado_maduracion = self._determinar_estado_maduracion(datos.nivel_maduracion)
        listo_cosechar = self._requiere_cosecha(datos)
        
        # Si no hay riesgos
        if not riesgos_detectados:
            return EstadoCelda(
                x=datos.x, y=datos.y,
                nivel_riesgo=NivelRiesgo.BAJO,
                tipo_amenaza="Normal",
                valor_riesgo=0.0,
                requiere_tratamiento=False,
                prioridad=1,
                estado_maduracion=estado_maduracion,
                frutos_disponibles=datos.frutos_disponibles,
                listo_para_cosechar=listo_cosechar
            )
        
        # Hay riesgos - seleccionar el más crítico
        riesgo_principal = max(riesgos_detectados, key=lambda r: r['valor'])
        nivel, prioridad, requiere = self._calcular_nivel_y_prioridad(
            riesgo_principal['valor'], 
            riesgo_principal['tipo']
        )
        
        return EstadoCelda(
            x=datos.x, y=datos.y,
            nivel_riesgo=nivel,
            tipo_amenaza=riesgo_principal['tipo'].value,
            valor_riesgo=riesgo_principal['valor'],
            requiere_tratamiento=requiere,
            prioridad=prioridad,
            estado_maduracion=estado_maduracion,
            frutos_disponibles=datos.frutos_disponibles,
            listo_para_cosechar=listo_cosechar
        )
    
    def _calcular_nivel_y_prioridad(self, valor: float, amenaza: TipoAmenaza) -> Tuple[NivelRiesgo, int, bool]:
        """Determina nivel de riesgo, prioridad y si requiere tratamiento"""
        if amenaza == TipoAmenaza.PLAGA:
            if valor >= 9.0:
                return (NivelRiesgo.CRITICO, 5, True)
            elif valor >= 7.0:
                return (NivelRiesgo.ALTO, 4, True)
            elif valor >= 5.0:
                return (NivelRiesgo.MEDIO, 3, True)
            else:
                return (NivelRiesgo.BAJO, 2, False)
        
        if valor >= 15.0:
            return (NivelRiesgo.CRITICO, 5, True)
        elif valor >= 10.0:
            return (NivelRiesgo.ALTO, 4, True)
        elif valor >= 5.0:
            return (NivelRiesgo.MEDIO, 3, False)
        else:
            return (NivelRiesgo.BAJO, 2, False)
    
    # ========================================================================
    # GENERACIÓN DE INSTRUCCIONES DE TRATAMIENTO
    # ========================================================================
    
    def _generar_instruccion_tratamiento(self, estado: EstadoCelda) -> InstruccionTratamiento:
        """Genera instrucción de tratamiento para el Agente Físico"""
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
        
        estados = list(self.mapa_estados.values())
        metricas = self._calcular_metricas()
        self._callback_agente_ui(estados, metricas)
    
    def _calcular_metricas(self) -> MetricasSistema:
        """Calcula métricas actuales del sistema"""
        frutos_totales = sum(e.frutos_disponibles for e in self.mapa_estados.values())
        frutos_listos = sum(
            e.frutos_disponibles 
            for e in self.mapa_estados.values() 
            if e.listo_para_cosechar
        )
        
        return MetricasSistema(
            tiempo_transcurrido=time.time() - self.tiempo_inicio,
            celdas_exploradas=len(self.celdas_exploradas),
            celdas_totales=self.celdas_totales,
            porcentaje_analizado=(len(self.celdas_exploradas) / self.celdas_totales) * 100,
            celdas_criticas=sum(1 for e in self.mapa_estados.values() if e.nivel_riesgo == NivelRiesgo.CRITICO),
            celdas_alto_riesgo=sum(1 for e in self.mapa_estados.values() if e.nivel_riesgo == NivelRiesgo.ALTO),
            tratamientos_ordenados=self.tratamientos_ordenados_total,
            frutos_totales_detectados=frutos_totales,
            frutos_listos_cosecha=frutos_listos,
            cosechas_ordenadas=self.cosechas_ordenadas_total,
            frutos_cosechados=self.frutos_cosechados_total
        )
    
    # ========================================================================
    # CONSULTAS PÚBLICAS
    # ========================================================================
    
    def obtener_estado_completo(self) -> Dict:
        """Retorna el estado completo del sistema"""
        return {
            'mapa_estados': self.mapa_estados,
            'metricas': self._calcular_metricas(),
            'cosechas_pendientes': self.cola_cosechas,
            'tratamientos_pendientes': self.cola_tratamientos,
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

COSECHA:
  • Frutos detectados: {metricas.frutos_totales_detectados}
  • Frutos listos para cosechar: {metricas.frutos_listos_cosecha}
  • Cosechas ordenadas: {metricas.cosechas_ordenadas}
  • Frutos cosechados: {metricas.frutos_cosechados} 🍅

ANÁLISIS DE RIESGOS:
  • Celdas críticas: {metricas.celdas_criticas}
  • Celdas alto riesgo: {metricas.celdas_alto_riesgo}
  • Tratamientos ordenados: {metricas.tratamientos_ordenados}

UMBRALES DE COSECHA:
"""
        for key, value in self.umbrales_cosecha.items():
            reporte += f"  • {key}: {value}\n"
        
        reporte += f"{'='*70}\n"
        return reporte


# ============================================================================
# EJEMPLO DE INTEGRACIÓN
# ============================================================================

def ejemplo_uso():
    """Ejemplo de cómo integrar el Manager con Agente Físico y UI"""
    print("\n" + "="*70)
    print("EJEMPLO - SISTEMA CON COSECHA Y TRATAMIENTO")
    print("="*70 + "\n")
    
    # ========================================================================
    # 1. CREAR MANAGER
    # ========================================================================
    manager = AgenteManager(grid_filas=10, grid_columnas=10)
    
    # ========================================================================
    # 2. AGENTE FÍSICO: Registrar callback
    # ========================================================================
    def agente_fisico_ejecutar(instruccion):
        """Esta función la implementa el equipo del Agente Físico"""
        if isinstance(instruccion, InstruccionCosecha):
            print(f"\n[Agente Físico] 🤖 COSECHA: {instruccion}")
            print(f"[Agente Físico] Moviendo a {instruccion.celda_objetivo}")
            print(f"[Agente Físico] Recolectando {instruccion.frutos_a_cosechar} jitomates")
            # Simular cosecha completada
            time.sleep(0.2)
            manager.reportar_cosecha_completada(instruccion.celda_objetivo, instruccion.frutos_a_cosechar)
            
        elif isinstance(instruccion, InstruccionTratamiento):
            print(f"\n[Agente Físico] 🤖 TRATAMIENTO: {instruccion}")
            print(f"[Agente Físico] Moviendo a {instruccion.celda_objetivo}")
            print(f"[Agente Físico] Aplicando: {instruccion.descripcion}")
    
    manager.registrar_agente_fisico(agente_fisico_ejecutar)
    
    # ========================================================================
    # 3. AGENTE UI: Registrar callback
    # ========================================================================
    def agente_ui_actualizar(estados: List[EstadoCelda], metricas: MetricasSistema):
        """Esta función la implementa el equipo de UI"""
        print(f"\n[Agente UI] 🖥️  Actualizando visualización")
        print(f"[Agente UI] Celdas: {len(estados)} | Progreso: {metricas.porcentaje_analizado:.1f}%")
        print(f"[Agente UI] Frutos listos: {metricas.frutos_listos_cosecha} | Cosechados: {metricas.frutos_cosechados}")
    
    manager.registrar_agente_ui(agente_ui_actualizar)
    
    # ========================================================================
    # 4. SIMULACIÓN: Agente Físico envía datos al explorar
    # ========================================================================
    print("\n--- SIMULANDO EXPLORACIÓN CON COSECHA ---\n")
    
    import random
    
    # Simular exploración de 8 celdas
    escenarios = [
        # Celda 1: Jitomates maduros, sin problemas
        DatosExploracion(
            x=1, y=1,
            temperatura=23.0, humedad=60.0,
            nivel_plagas=2.0, nivel_nutrientes=7.0,
            nivel_maduracion=8.5, tamano_fruto=7.5,
            color_rgb=(255, 50, 50), frutos_disponibles=12
        ),
        # Celda 2: Jitomates sobre maduros (urgente!)
        DatosExploracion(
            x=3, y=2,
            temperatura=24.0, humedad=55.0,
            nivel_plagas=1.5, nivel_nutrientes=8.0,
            nivel_maduracion=9.8, tamano_fruto=8.0,
            color_rgb=(200, 20, 20), frutos_disponibles=8
        ),
        # Celda 3: Jitomates verdes con plagas
        DatosExploracion(
            x=5, y=3,
            temperatura=22.0, humedad=58.0,
            nivel_plagas=8.0, nivel_nutrientes=6.0,
            nivel_maduracion=3.0, tamano_fruto=4.0,
            color_rgb=(100, 180, 80), frutos_disponibles=15
        ),
        # Celda 4: Jitomates maduros pero con sequía
        DatosExploracion(
            x=7, y=4,
            temperatura=28.0, humedad=25.0,
            nivel_plagas=2.0, nivel_nutrientes=5.0,
            nivel_maduracion=7.5, tamano_fruto=6.5,
            color_rgb=(255, 80, 60), frutos_disponibles=10
        ),
        # Celda 5: Jitomates en maduración, todo normal
        DatosExploracion(
            x=2, y=6,
            temperatura=22.0, humedad=62.0,
            nivel_plagas=1.0, nivel_nutrientes=7.5,
            nivel_maduracion=5.5, tamano_fruto=6.0,
            color_rgb=(200, 150, 100), frutos_disponibles=18
        ),
        # Celda 6: Jitomates maduros óptimos
        DatosExploracion(
            x=8, y=7,
            temperatura=23.5, humedad=58.0,
            nivel_plagas=1.5, nivel_nutrientes=7.0,
            nivel_maduracion=9.0, tamano_fruto=7.8,
            color_rgb=(255, 40, 40), frutos_disponibles=14
        ),
        # Celda 7: Sin frutos, solo plantas con nutrientes bajos
        DatosExploracion(
            x=4, y=8,
            temperatura=24.0, humedad=60.0,
            nivel_plagas=2.0, nivel_nutrientes=3.0,
            nivel_maduracion=0.0, tamano_fruto=0.0,
            color_rgb=(80, 150, 70), frutos_disponibles=0
        ),
        # Celda 8: Jitomates maduros con temperatura alta
        DatosExploracion(
            x=9, y=9,
            temperatura=33.0, humedad=62.0,
            nivel_plagas=2.5, nivel_nutrientes=6.5,
            nivel_maduracion=8.0, tamano_fruto=7.0,
            color_rgb=(255, 60, 50), frutos_disponibles=11
        ),
    ]
    
    for datos in escenarios:
        print(f"\n{'='*70}")
        print(f"[Agente Físico] 📍 Explorando celda ({datos.x}, {datos.y})")
        print(f"[Agente Físico] 🌡️  T={datos.temperatura:.1f}°C | H={datos.humedad:.1f}%")
        print(f"[Agente Físico] 🐛 Plagas={datos.nivel_plagas:.1f} | 🌿 Nutrientes={datos.nivel_nutrientes:.1f}")
        print(f"[Agente Físico] 🍅 Frutos: {datos.frutos_disponibles} | Maduración: {datos.nivel_maduracion:.1f}/10")
        
        # ENVIAR DATOS AL MANAGER
        manager.recibir_datos_exploracion(datos)
        
        time.sleep(0.3)
    
    # ========================================================================
    # 5. REPORTE FINAL
    # ========================================================================
    print("\n" + manager.generar_reporte())
    
    # Mostrar colas de instrucciones
    print("\n📋 RESUMEN DE INSTRUCCIONES GENERADAS:\n")
    
    if manager.cola_cosechas:
        print("🍅 COSECHAS (ordenadas por prioridad):")
        cosechas_ordenadas = sorted(manager.cola_cosechas, key=lambda c: c.prioridad, reverse=True)
        for i, cosecha in enumerate(cosechas_ordenadas, 1):
            print(f"  {i}. {cosecha}")
    
    if manager.cola_tratamientos:
        print("\n⚠️  TRATAMIENTOS (ordenados por urgencia):")
        tratamientos_ordenados = sorted(manager.cola_tratamientos, key=lambda t: t.nivel_urgencia, reverse=True)
        for i, tratamiento in enumerate(tratamientos_ordenados, 1):
            print(f"  {i}. {tratamiento}")
    
    print("\n" + "="*70)
    print("✅ SIMULACIÓN COMPLETADA")
    print("="*70)


# ============================================================================
# GUÍA RÁPIDA PARA INTEGRACIÓN
# ============================================================================

def guia_integracion():
    """
    Guía rápida de cómo usar el Manager en tu equipo
    """
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║               GUÍA DE INTEGRACIÓN - AGENTE MANAGER                   ║
╚══════════════════════════════════════════════════════════════════════╝

📦 IMPORTAR:
───────────
from manager import (
    AgenteManager, 
    DatosExploracion, 
    InstruccionCosecha, 
    InstruccionTratamiento,
    EstadoCelda,
    MetricasSistema
)

👤 PARA EL AGENTE FÍSICO:
─────────────────────────
1. Crear manager:
   manager = AgenteManager(grid_filas=10, grid_columnas=10)

2. Registrar tu función que ejecuta instrucciones:
   def ejecutar_instruccion(instruccion):
       if isinstance(instruccion, InstruccionCosecha):
           # Tu código: ir a celda y cosechar
           # Después de cosechar, notificar:
           manager.reportar_cosecha_completada(
               instruccion.celda_objetivo, 
               instruccion.frutos_a_cosechar
           )
       
       elif isinstance(instruccion, InstruccionTratamiento):
           # Tu código: ir a celda y aplicar tratamiento
           pass
   
   manager.registrar_agente_fisico(ejecutar_instruccion)

3. Mientras exploras, envía datos:
   datos = DatosExploracion(
       x=pos_x, y=pos_y,
       temperatura=leer_temp(),
       humedad=leer_humedad(),
       nivel_plagas=detectar_plagas(),
       nivel_nutrientes=analizar_nutrientes(),
       nivel_maduracion=analizar_maduracion(),  # 0-10
       tamano_fruto=medir_tamano(),             # 0-10
       color_rgb=(R, G, B),
       frutos_disponibles=contar_frutos(),
       agente_id=mi_id
   )
   
   manager.recibir_datos_exploracion(datos)

🖥️ PARA EL AGENTE UI:
─────────────────────
1. Registrar tu función de actualización:
   def actualizar_interfaz(estados, metricas):
       # estados: List[EstadoCelda]
       # metricas: MetricasSistema
       
       for estado in estados:
           # Pintar celda según:
           # - estado.nivel_riesgo (color)
           # - estado.estado_maduracion
           # - estado.frutos_disponibles
           # - estado.listo_para_cosechar
           pintar_celda(estado.x, estado.y, estado)
       
       # Actualizar panel con:
       # - metricas.frutos_listos_cosecha
       # - metricas.frutos_cosechados
       # - metricas.cosechas_ordenadas
       # - metricas.tratamientos_ordenados
       actualizar_panel(metricas)
   
   manager.registrar_agente_ui(actualizar_interfaz)

🎯 PRIORIZACIÓN AUTOMÁTICA:
──────────────────────────
El Manager prioriza automáticamente:
1. 🍅 COSECHA (Prioridad 5): Frutos sobre maduros (>9.5)
2. 🍅 COSECHA (Prioridad 4): Frutos óptimos (8.5-9.5)
3. ⚠️  TRATAMIENTO (Prioridad 5): Plagas críticas
4. 🍅 COSECHA (Prioridad 3): Frutos maduros (7-8.5)
5. ⚠️  TRATAMIENTO (Prioridad 4): Problemas altos

⚙️ PERSONALIZAR UMBRALES:
─────────────────────────
# Umbrales de cosecha:
manager.configurar_umbrales_cosecha({
    'maduracion_minima': 7.0,
    'maduracion_optima': 8.5,
    'maduracion_sobre': 9.5,
    'tamano_minimo': 5.0
})

# Umbrales de riesgo:
manager.configurar_umbrales({
    'temperatura_min': 18.0,
    'temperatura_max': 28.0,
    'nivel_plagas_critico': 8.0
})

📊 CONSULTAR ESTADO:
────────────────────
# Obtener estado completo:
estado = manager.obtener_estado_completo()

# Generar reporte:
print(manager.generar_reporte())

╔══════════════════════════════════════════════════════════════════════╗
║  ✅ El Manager se encarga de toda la lógica de decisión              ║
║  ✅ Los otros componentes solo ejecutan las instrucciones            ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    guia_integracion()
    print("\n")
    ejemplo_uso()