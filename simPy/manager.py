# -*- coding: utf-8 -*-
"""
AGENTE MANAGER CON COORDINACION MULTI-AGENTE Y CAPATAZ
=======================================================

Responsabilidades:
1. Recibir datos de riesgo de los agentes exploradores
2. Evaluar riesgos con umbrales y reglas
3. Detectar jitomates listos para cosechar
4. Establecer prioridades y protocolo de accion
5. Enviar instrucciones de COSECHA y TRATAMIENTO al Agente Fisico
6. Enviar informacion de estado al Agente UI
7. COORDINAR 5 AGENTES FISICOS trabajando en paralelo
8. INTEGRAR AL CAPATAZ como supervisor
"""

from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
from threading import Thread, Lock

# Importar Capataz
from capataz import AgenteCapataz, TipoOrden


class NivelRiesgo(Enum):
    """Niveles de riesgo para el analisis"""
    SIN_DATOS = 0
    BAJO = 1
    MEDIO = 2
    ALTO = 3
    CRITICO = 4


class TipoAmenaza(Enum):
    """Tipos de amenazas detectables"""
    PLAGA = "Plaga"
    HONGO = "Hongo"
    SEQUIA = "Sequia"
    EXCESO_AGUA = "Exceso de agua"
    NUTRIENTES_BAJOS = "Nutrientes bajos"
    TEMPERATURA_ALTA = "Temperatura alta"
    TEMPERATURA_BAJA = "Temperatura baja"


class EstadoMaduracion(Enum):
    """Estados de maduracion de los jitomates"""
    VERDE = "Verde"
    EN_MADURACION = "En maduracion"
    MADURO = "Maduro"
    SOBRE_MADURO = "Sobre maduro"


@dataclass
class DatosExploracion:
    """Datos que envia el Agente Fisico al Manager"""
    x: int
    y: int
    temperatura: float
    humedad: float
    nivel_plagas: float
    nivel_nutrientes: float
    nivel_maduracion: float
    tamano_fruto: float
    color_rgb: Tuple[int, int, int]
    frutos_disponibles: int
    timestamp: datetime = field(default_factory=datetime.now)
    agente_id: int = 0


@dataclass
class InstruccionCosecha:
    """Instruccion de COSECHA para el Agente Fisico"""
    celda_objetivo: Tuple[int, int]
    frutos_a_cosechar: int
    nivel_maduracion: float
    prioridad: int
    descripcion: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"Cosecha en {self.celda_objetivo}: {self.frutos_a_cosechar} frutos (Prioridad: {self.prioridad})"


@dataclass
class InstruccionTratamiento:
    """Instruccion de TRATAMIENTO para el Agente Fisico"""
    celda_objetivo: Tuple[int, int]
    tipo_tratamiento: str
    nivel_urgencia: int
    tipo_amenaza: str
    descripcion: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"Tratamiento en {self.celda_objetivo}: {self.tipo_tratamiento} (Urgencia: {self.nivel_urgencia})"


@dataclass
class EstadoCelda:
    """Estado procesado de una celda para la UI"""
    x: int
    y: int
    nivel_riesgo: NivelRiesgo
    tipo_amenaza: str
    valor_riesgo: float
    requiere_tratamiento: bool
    prioridad: int
    estado_maduracion: EstadoMaduracion
    frutos_disponibles: int
    listo_para_cosechar: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricasSistema:
    """Metricas del sistema para la UI"""
    tiempo_transcurrido: float = 0.0
    celdas_exploradas: int = 0
    celdas_totales: int = 0
    porcentaje_analizado: float = 0.0
    celdas_criticas: int = 0
    celdas_alto_riesgo: int = 0
    tratamientos_ordenados: int = 0
    frutos_totales_detectados: int = 0
    frutos_listos_cosecha: int = 0
    cosechas_ordenadas: int = 0
    frutos_cosechados: int = 0
    agentes_activos: int = 0
    agentes_explorando: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


# AGENTE MANAGER CON COORDINACION Y CAPATAZ

class AgenteManager:
    """
    Agente Manager: Núcleo de decision y coordinacion del sistema
    
    RESPONSABILIDADES:
    - Crear y coordinar múltiples agentes fisicos
    - Distribuir trabajo entre agentes
    - Asignar instrucciones al agente mas apropiado
    - Monitorear estado de todos los agentes
    - INTEGRAR AL CAPATAZ como supervisor
    """
    
    def __init__(self, grid_filas: int = 10, grid_columnas: int = 10, num_agentes: int = 5):
        """
        Inicializa el Agente Manager con coordinacion multi-agente y capataz
        
        Args:
            grid_filas: Número de filas del cultivo
            grid_columnas: Número de columnas del cultivo
            num_agentes: Número de agentes fisicos a coordinar
        """
        # Configuracion del grid
        self.grid_filas = grid_filas
        self.grid_columnas = grid_columnas
        self.celdas_totales = grid_filas * grid_columnas
        self.num_agentes = num_agentes
        
        # Almacenamiento de datos
        self.mapa_estados: Dict[Tuple[int, int], EstadoCelda] = {}
        self.datos_crudos: Dict[Tuple[int, int], DatosExploracion] = {}
        
        # Colas de instrucciones separadas
        self.cola_cosechas: List[InstruccionCosecha] = []
        self.cola_tratamientos: List[InstruccionTratamiento] = []
        
        # Control de exploracion
        self.celdas_exploradas: set = set()
        
        # Control de agentes fisicos
        self.agentes_fisicos: List = []
        self.agentes_threads: List[Thread] = []
        self.lock_agentes = Lock()
        
        # Metricas
        self.tiempo_inicio = time.time()
        self.cosechas_ordenadas_total = 0
        self.tratamientos_ordenados_total = 0
        self.frutos_cosechados_total = 0
        
        # Callbacks
        self._callback_agente_ui: Optional[Callable] = None
        
        # Umbrales
        self.umbrales = {
            'temperatura_min': 15.0,
            'temperatura_max': 30.0,
            'humedad_min': 40.0,
            'humedad_max': 80.0,
            'nivel_plagas_critico': 7.0,
            'nivel_plagas_alto': 5.0,
            'nivel_nutrientes_bajo': 4.0,
        }
        
        self.umbrales_cosecha = {
            'maduracion_minima': 7.0,
            'maduracion_optima': 8.5,
            'maduracion_sobre': 9.5,
            'tamano_minimo': 5.0,
        }
        
        # NUEVO: Crear Agente Capataz
        self.capataz = AgenteCapataz(
            posicion_observacion=(0, 0),
            num_agentes=num_agentes
        )
        
        print(f"[Manager] Inicializado - Grid: {grid_filas}x{grid_columnas}")
        print(f"[Manager] Coordinando {num_agentes} agentes fisicos")
        print(f"[Manager] [CAPATAZ] Capataz asignado en posicion {self.capataz.posicion}")
    
    # ========================================================================
    # COORDINACION MULTI-AGENTE
    # ========================================================================
    
    def crear_agentes_fisicos(self):
        """
        Crea los agentes fisicos y los configura con el capataz
        
        IMPORTANTE: Debe llamarse ANTES de iniciar_exploracion_multi_agente()
        """
        from fisico import AgenteFisico, ConfiguracionAgente
        
        print(f"\n[Manager] [AGENTES] Creando {self.num_agentes} agentes fisicos...")
        
        for i in range(1, self.num_agentes + 1):
            agente = AgenteFisico(
                agente_id=i,
                callback_enviar_datos=self.recibir_datos_exploracion,
                callback_reportar_cosecha=self.reportar_cosecha_completada,
                callback_actualizar_capataz=self._actualizar_capataz,
                config=ConfiguracionAgente(agente_id=i)
            )
            self.agentes_fisicos.append(agente)
        
        print(f"[Manager] [OK] {self.num_agentes} agentes creados")
        print(f"[Manager] [CONEXION] Agentes conectados con el Capataz")
    
    def distribuir_trabajo(self):
        """
        Distribuye las celdas del grid entre los agentes
        
        Estrategia: Division por filas para minimizar desplazamientos
        """
        if not self.agentes_fisicos:
            print("[Manager] [ADVERTENCIA] Error: No hay agentes creados. Llama crear_agentes_fisicos() primero")
            return
        
        print(f"\n[Manager] [INFO] Distribuyendo trabajo entre {self.num_agentes} agentes...")
        
        # Generar todas las celdas
        todas_celdas = [
            (x, y) 
            for x in range(self.grid_filas) 
            for y in range(self.grid_columnas)
        ]
        
        # Dividir equitativamente
        celdas_por_agente = len(todas_celdas) // self.num_agentes
        
        for i, agente in enumerate(self.agentes_fisicos):
            inicio = i * celdas_por_agente
            fin = inicio + celdas_por_agente if i < self.num_agentes - 1 else len(todas_celdas)
            celdas_asignadas = todas_celdas[inicio:fin]
            agente.asignar_celdas(celdas_asignadas)
        
        print(f"[Manager] [OK] Trabajo distribuido")
    
    def iniciar_exploracion_multi_agente(self):
        """
        Inicia la exploracion con todos los agentes en paralelo
        El capataz supervisara automaticamente
        """
        if not self.agentes_fisicos:
            print("[Manager] [ADVERTENCIA] Error: Primero llama crear_agentes_fisicos() y distribuir_trabajo()")
            return
        
        print(f"\n[Manager] [INIT] Iniciando exploracion multi-agente")
        print(f"[Manager] {self.num_agentes} agentes trabajando en paralelo")
        print(f"[Manager] [CAPATAZ] Capataz supervisando desde {self.capataz.posicion}\n")
        
        # Crear threads para cada agente
        self.agentes_threads = []
        for agente in self.agentes_fisicos:
            thread = Thread(target=agente.iniciar_exploracion)
            thread.start()
            self.agentes_threads.append(thread)
        
        # Esperar que todos terminen
        for thread in self.agentes_threads:
            thread.join()
        
        print(f"\n[Manager] [OK] Exploracion multi-agente completada")
        self._mostrar_resumen_agentes()
    
    def _asignar_instruccion_a_agente(self, instruccion):
        """
        Asigna una instruccion al agente mas apropiado
        """
        if not self.agentes_fisicos:
            return
        
        # Asignar al primer agente disponible
        for agente in self.agentes_fisicos:
            if not agente.procesando_instruccion and agente.activo:
                agente.recibir_instruccion(instruccion)
                break
    
    def _mostrar_resumen_agentes(self):
        """Muestra resumen del trabajo de todos los agentes"""
        print(f"\n{'='*70}")
        print("RESUMEN DE AGENTES FISICOS")
        print(f"{'='*70}")
        
        total_celdas = 0
        total_cosechas = 0
        total_tratamientos = 0
        
        for agente in self.agentes_fisicos:
            stats = agente.obtener_estadisticas()
            total_celdas += stats['celdas_exploradas']
            total_cosechas += stats['cosechas_completadas']
            total_tratamientos += stats['tratamientos_completados']
            
            print(f"\n[AGENTES] Agente {stats['agente_id']}:")
            print(f"   [BUSQUEDA] Celdas exploradas: {stats['celdas_exploradas']}")
            print(f"   [FRUTOS] Cosechas: {stats['cosechas_completadas']}")
            print(f"   [ADVERTENCIA] Tratamientos: {stats['tratamientos_completados']}")
            print(f"   🔋 Bateria: {stats['bateria']:.1f}%")
            print(f"   [TRABAJO] Frutos cargados: {stats['frutos_cargados']}")
            print(f"   [DATOS] Estado: {stats['estado_capataz']}")
        
        print(f"\n{'='*70}")
        print(f"TOTALES:")
        print(f"   [BUSQUEDA] Celdas exploradas: {total_celdas}/{self.celdas_totales}")
        print(f"   [FRUTOS] Total cosechas: {total_cosechas}")
        print(f"   [ADVERTENCIA] Total tratamientos: {total_tratamientos}")
        print(f"{'='*70}\n")
    
    # ========================================================================
    # INTEGRACION CON EL CAPATAZ
    # ========================================================================
    
    def _actualizar_capataz(
        self,
        agente_id: int,
        posicion: Tuple[int, int],
        bateria: float,
        frutos_cargados: int,
        estado: str,
        celdas_exploradas: int,
        cosechas_completadas: int
    ):
        """
        Callback para que agentes notifiquen al capataz
        """
        self.capataz.actualizar_estado_agente(
            agente_id=agente_id,
            posicion=posicion,
            bateria=bateria,
            frutos_cargados=frutos_cargados,
            estado=estado,
            celdas_exploradas=celdas_exploradas,
            cosechas_completadas=cosechas_completadas
        )
    
    def _enviar_orden_capataz_a_agente(self, orden):
        """
        Envia una orden del capataz a un agente especifico
        """
        agente = next((a for a in self.agentes_fisicos if a.agente_id == orden.agente_destino), None)
        if agente:
            agente.recibir_orden_capataz(orden.tipo_orden, orden.razon)
    
    # ========================================================================
    # RECEPCION Y PROCESAMIENTO DE DATOS
    # ========================================================================
    
    def registrar_agente_ui(self, callback: Callable[[List[EstadoCelda], MetricasSistema], None]):
        """Registra el callback para comunicarse con el Agente UI"""
        self._callback_agente_ui = callback
        print("[Manager] Agente UI registrado")
    
    def recibir_datos_exploracion(self, datos: DatosExploracion):
        """
        Recibe datos del Agente Fisico (llamado por callback)
        """
        pos = (datos.x, datos.y)
        
        # Almacenar datos
        self.datos_crudos[pos] = datos
        self.celdas_exploradas.add(pos)
        
        # REPORTAR CONTAMINACION AL CAPATAZ
        if datos.nivel_plagas > 5.0:
            self.capataz.reportar_contaminacion(
                celda=(datos.x, datos.y),
                nivel=datos.nivel_plagas
            )
        
        # Evaluar COSECHA
        if self._requiere_cosecha(datos):
            instruccion_cosecha = self._generar_instruccion_cosecha(datos)
            self.cola_cosechas.append(instruccion_cosecha)
            self.cosechas_ordenadas_total += 1
            self._asignar_instruccion_a_agente(instruccion_cosecha)
            print(f"[Manager] [FRUTOS] COSECHA ordenada: {instruccion_cosecha}")
        
        # Evaluar RIESGOS
        estado_celda = self._evaluar_riesgo(datos)
        self.mapa_estados[pos] = estado_celda
        
        print(f"[Manager] Celda ({datos.x}, {datos.y}) - Riesgo: {estado_celda.nivel_riesgo.name} | Maduracion: {estado_celda.estado_maduracion.name}")
        
        # Generar tratamiento si necesario
        if estado_celda.requiere_tratamiento:
            instruccion_tratamiento = self._generar_instruccion_tratamiento(estado_celda)
            self.cola_tratamientos.append(instruccion_tratamiento)
            self.tratamientos_ordenados_total += 1
            self._asignar_instruccion_a_agente(instruccion_tratamiento)
            print(f"[Manager] [ADVERTENCIA] TRATAMIENTO ordenado: {instruccion_tratamiento}")
        
        # Actualizar UI
        self._notificar_ui()
    
    def reportar_cosecha_completada(self, celda: Tuple[int, int], frutos_cosechados: int):
        """El Agente Fisico llama esto despues de cosechar"""
        self.frutos_cosechados_total += frutos_cosechados
        print(f"[Manager] [OK] Cosecha completada en {celda}: {frutos_cosechados} frutos")
        print(f"[Manager] Total cosechado: {self.frutos_cosechados_total} frutos")
        self._notificar_ui()
    
    # ========================================================================
    # EVALUACION Y DECISION
    # ========================================================================
    
    def _requiere_cosecha(self, datos: DatosExploracion) -> bool:
        return (
            datos.frutos_disponibles > 0 and
            datos.nivel_maduracion >= self.umbrales_cosecha['maduracion_minima'] and
            datos.tamano_fruto >= self.umbrales_cosecha['tamano_minimo']
        )
    
    def _generar_instruccion_cosecha(self, datos: DatosExploracion) -> InstruccionCosecha:
        maduracion = datos.nivel_maduracion
        
        if maduracion >= self.umbrales_cosecha['maduracion_sobre']:
            prioridad = 5
            descripcion = "URGENTE: Frutos sobre maduros"
        elif maduracion >= self.umbrales_cosecha['maduracion_optima']:
            prioridad = 4
            descripcion = "Frutos en punto optimo"
        else:
            prioridad = 3
            descripcion = "Frutos maduros listos"
        
        return InstruccionCosecha(
            celda_objetivo=(datos.x, datos.y),
            frutos_a_cosechar=datos.frutos_disponibles,
            nivel_maduracion=maduracion,
            prioridad=prioridad,
            descripcion=descripcion
        )
    
    def _evaluar_riesgo(self, datos: DatosExploracion) -> EstadoCelda:
        """Evalúa riesgo"""
        riesgos = []
        
        if datos.temperatura < self.umbrales['temperatura_min']:
            riesgos.append({'tipo': TipoAmenaza.TEMPERATURA_BAJA, 'valor': 5.0})
        elif datos.temperatura > self.umbrales['temperatura_max']:
            riesgos.append({'tipo': TipoAmenaza.TEMPERATURA_ALTA, 'valor': 5.0})
        
        if datos.nivel_plagas >= self.umbrales['nivel_plagas_critico']:
            riesgos.append({'tipo': TipoAmenaza.PLAGA, 'valor': datos.nivel_plagas})
        
        estado_maduracion = self._determinar_estado_maduracion(datos.nivel_maduracion)
        listo_cosechar = self._requiere_cosecha(datos)
        
        if not riesgos:
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
        
        riesgo_principal = max(riesgos, key=lambda r: r['valor'])
        return EstadoCelda(
            x=datos.x, y=datos.y,
            nivel_riesgo=NivelRiesgo.ALTO,
            tipo_amenaza=riesgo_principal['tipo'].value,
            valor_riesgo=riesgo_principal['valor'],
            requiere_tratamiento=True,
            prioridad=4,
            estado_maduracion=estado_maduracion,
            frutos_disponibles=datos.frutos_disponibles,
            listo_para_cosechar=listo_cosechar
        )
    
    def _determinar_estado_maduracion(self, nivel: float) -> EstadoMaduracion:
        if nivel >= self.umbrales_cosecha['maduracion_sobre']:
            return EstadoMaduracion.SOBRE_MADURO
        elif nivel >= self.umbrales_cosecha['maduracion_minima']:
            return EstadoMaduracion.MADURO
        elif nivel >= 4.0:
            return EstadoMaduracion.EN_MADURACION
        else:
            return EstadoMaduracion.VERDE
    
    def _generar_instruccion_tratamiento(self, estado: EstadoCelda) -> InstruccionTratamiento:
        return InstruccionTratamiento(
            celda_objetivo=(estado.x, estado.y),
            tipo_tratamiento='aplicar_tratamiento',
            nivel_urgencia=estado.prioridad,
            tipo_amenaza=estado.tipo_amenaza,
            descripcion=f"Tratar {estado.tipo_amenaza}"
        )
    
    def _notificar_ui(self):
        """Envia actualizacion al Agente UI"""
        if not self._callback_agente_ui:
            return
        
        estados = list(self.mapa_estados.values())
        metricas = self._calcular_metricas()
        self._callback_agente_ui(estados, metricas)
    
    def _calcular_metricas(self) -> MetricasSistema:
        """Calcula metricas con info multi-agente"""
        frutos_totales = sum(e.frutos_disponibles for e in self.mapa_estados.values())
        frutos_listos = sum(
            e.frutos_disponibles 
            for e in self.mapa_estados.values() 
            if e.listo_para_cosechar
        )
        
        agentes_explorando = sum(1 for a in self.agentes_fisicos if a.activo and not a.exploracion_completa)
        
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
            frutos_cosechados=self.frutos_cosechados_total,
            agentes_activos=len(self.agentes_fisicos),
            agentes_explorando=agentes_explorando
        )
    
    def generar_reporte(self) -> str:
        """Genera reporte con metricas multi-agente y capataz"""
        metricas = self._calcular_metricas()
        
        reporte = f"""
{'='*70}
REPORTE DEL SISTEMA - AGENTE MANAGER
{'='*70}

AGENTES FISICOS:
  • Total agentes: {metricas.agentes_activos}
  • Agentes explorando: {metricas.agentes_explorando}

EXPLORACION:
  • Celdas exploradas: {metricas.celdas_exploradas}/{metricas.celdas_totales}
  • Progreso: {metricas.porcentaje_analizado:.1f}%
  • Tiempo: {metricas.tiempo_transcurrido:.1f}s

COSECHA:
  • Frutos detectados: {metricas.frutos_totales_detectados}
  • Listos para cosechar: {metricas.frutos_listos_cosecha}
  • Cosechas ordenadas: {metricas.cosechas_ordenadas}
  • Frutos cosechados: {metricas.frutos_cosechados} [FRUTOS]

RIESGOS:
  • Celdas criticas: {metricas.celdas_criticas}
  • Alto riesgo: {metricas.celdas_alto_riesgo}
  • Tratamientos ordenados: {metricas.tratamientos_ordenados}

{'='*70}
"""
        
        # Agregar reporte del capataz
        reporte += f"\n{self.capataz.generar_reporte_final()}"
        
        return reporte