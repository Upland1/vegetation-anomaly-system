"""
AGENTE CAPATAZ (MANAGER)
========================
El "Ojo" que todo lo ve. Coordina recolectores y detecta amenazas críticas (Gusano).
"""

from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
from threading import Thread, Lock, Event

# --- ENUMS Y ESTRUCTURAS DE DATOS ---

class OrdenCapataz(Enum):
    """Las órdenes que el Capataz puede dar"""
    CONTINUAR = "CONTINUA"    # Estado normal
    PARAR = "PARATE"          # Pausa temporal
    ABANDONAR = "ABANDONA"    # Cancelación de emergencia

class NivelRiesgo(Enum):
    SIN_DATOS = 0
    BAJO = 1
    MEDIO = 2
    ALTO = 3
    CRITICO = 4 # Aquí vive el Gusano

class EstadoMaduracion(Enum):
    VERDE = "Verde"
    EN_MADURACION = "En maduración"
    MADURO = "Maduro"
    SOBRE_MADURO = "Sobre maduro"

@dataclass
class DatosExploracion:
    x: int
    y: int
    temperatura: float
    humedad: float
    nivel_plagas: float # > 8.0 es el GUSANO
    nivel_nutrientes: float
    nivel_maduracion: float
    frutos_disponibles: int
    agente_id: int
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InstruccionCosecha:
    celda_objetivo: Tuple[int, int]
    frutos_a_cosechar: int
    prioridad: int
    descripcion: str

@dataclass
class EstadoCelda:
    x: int
    y: int
    nivel_riesgo: NivelRiesgo
    tipo_amenaza: str
    frutos_disponibles: int
    listo_para_cosechar: bool
    tiene_gusano: bool = False # Flag específico para el gusano

@dataclass
class EstadoAgenteVisibilidad:
    """Información para que la UI pinte al agente y sus órdenes"""
    id: int
    x: int
    y: int
    orden_actual: OrdenCapataz
    bateria: float
    cargando_frutos: int

@dataclass
class MetricasSistema:
    tiempo_transcurrido: float = 0.0
    celdas_exploradas: int = 0
    celdas_totales: int = 0
    frutos_cosechados: int = 0
    agentes_activos: int = 0
    amenazas_gusano: int = 0 # Contador de gusanos

# --- CLASE PRINCIPAL ---

class AgenteCapataz:
    """
    El Capataz: Observa, evalúa riesgos críticos y da órdenes imperativas.
    """
    
    def __init__(self, grid_filas: int = 10, grid_columnas: int = 10, num_agentes: int = 3):
        self.grid_filas = grid_filas
        self.grid_columnas = grid_columnas
        self.num_agentes = num_agentes
        
        # Datos del huerto
        self.mapa_estados: Dict[Tuple[int, int], EstadoCelda] = {}
        self.cola_cosechas: List[InstruccionCosecha] = []
        self.celdas_exploradas: set = set()
        
        # Gestión de Agentes Físicos
        self.agentes_fisicos = []
        # Diccionario para controlar los hilos de los agentes
        # Key: agente_id, Value: {'evento_pausa': Event, 'flag_abortar': bool, 'orden_actual': OrdenCapataz}
        self.controles_agentes = {}
        
        # Métricas
        self.tiempo_inicio = time.time()
        self.frutos_cosechados_total = 0
        self.contador_gusanos = 0
        
        # Callback UI
        self._callback_ui: Optional[Callable] = None
        
        print(f"[Capataz] 👁️ Observando huerto {grid_filas}x{grid_columnas}")

    def registrar_agente_ui(self, callback):
        self._callback_ui = callback

    def crear_agentes_fisicos(self):
        from fisico import AgenteFisico # Import local para evitar ciclo
        
        print(f"[Capataz] 📢 Contratando {self.num_agentes} recolectores...")
        for i in range(1, self.num_agentes + 1):
            # Crear controles de sincronización
            evento_pausa = Event()
            evento_pausa.set() # Empieza en verde (Set = True = Continua)
            
            self.controles_agentes[i] = {
                'evento': evento_pausa,
                'abortar': False,
                'orden_texto': OrdenCapataz.CONTINUAR
            }
            
            # Instanciar agente inyectándole sus controles
            agente = AgenteFisico(
                agente_id=i,
                callback_datos=self.recibir_datos,
                callback_cosecha=self.reportar_cosecha,
                control_evento=evento_pausa,
                control_abortar=lambda id=i: self.controles_agentes[id]['abortar']
            )
            self.agentes_fisicos.append(agente)

    def distribuir_trabajo(self):
        # Distribución simple por franjas
        celdas = [(r, c) for r in range(self.grid_filas) for c in range(self.grid_columnas)]
        chunk = len(celdas) // self.num_agentes
        for i, agente in enumerate(self.agentes_fisicos):
            start = i * chunk
            end = start + chunk if i < self.num_agentes - 1 else len(celdas)
            agente.asignar_celdas(celdas[start:end])

    def iniciar_jornada(self):
        threads = []
        for agente in self.agentes_fisicos:
            t = Thread(target=agente.iniciar_trabajo)
            t.start()
            threads.append(t)
        
        # Esperamos a los hilos (esto bloquearía, así que lo hacemos en main usualmente)
        # Aquí solo retornamos los threads para que main los gestione
        return threads

    # --- LÓGICA DE ÓRDENES DEL CAPATAZ ---

    def emitir_orden(self, agente_id: int, orden: OrdenCapataz):
        """Emite una de las 3 órdenes sagradas"""
        ctrl = self.controles_agentes[agente_id]
        ctrl['orden_texto'] = orden
        
        if orden == OrdenCapataz.PARAR:
            ctrl['evento'].clear() # Bloquea el thread del agente
            print(f"[Capataz] ✋ ORDEN: ¡Agente {agente_id}, PARATE!")
            
        elif orden == OrdenCapataz.CONTINUAR:
            ctrl['abortar'] = False
            ctrl['evento'].set()   # Desbloquea el thread
            print(f"[Capataz] 👉 ORDEN: Agente {agente_id}, CONTINUA.")
            
        elif orden == OrdenCapataz.ABANDONAR:
            ctrl['abortar'] = True # Activa bandera de aborto
            ctrl['evento'].set()   # Asegura que corra para leer la bandera
            print(f"[Capataz] ⚠️ ORDEN: ¡Agente {agente_id}, ABANDONA LA RECOLECCIÓN!")

    # --- RECEPCIÓN DE DATOS ---

    def recibir_datos(self, datos: DatosExploracion):
        """El agente envía datos. El Capataz busca al GUSANO."""
        
        # 1. Análisis de Riesgo (Buscando al Gusano)
        tiene_gusano = False
        nivel_riesgo = NivelRiesgo.BAJO
        
        if datos.nivel_plagas > 8.0:
            tiene_gusano = True
            nivel_riesgo = NivelRiesgo.CRITICO
            self.contador_gusanos += 1
            print(f"[Capataz] 🐛 ¡GUSANO DETECTADO EN ({datos.x}, {datos.y})! Nivel: {datos.nivel_plagas:.1f}")
            
            # --- ACCIÓN DEL CAPATAZ ---
            # Si hay gusano, ordena ABANDONAR al agente que lo vio
            self.emitir_orden(datos.agente_id, OrdenCapataz.ABANDONAR)
            
            # Opcional: Parar a los vecinos por seguridad (ejemplo de lógica compleja)
            # self.emitir_orden(otro_agente_id, OrdenCapataz.PARAR)

        # 2. Análisis de Cosecha
        listo_cosecha = (datos.frutos_disponibles > 0 and 
                         datos.nivel_maduracion > 7.0 and 
                         not tiene_gusano) # No cosechar si hay gusano

        if listo_cosecha:
            # Crear instrucción (aunque el agente autónomo ya lo sabe, el manager lo registra)
            instr = InstruccionCosecha((datos.x, datos.y), datos.frutos_disponibles, 1, "Cosecha standard")
            self.cola_cosechas.append(instr)
            # Aquí podríamos asignar la tarea a otro agente si este está ocupado
            # pero asumiremos que el explorador cosecha lo que encuentra por ahora.

        # 3. Guardar Estado
        estado = EstadoCelda(
            x=datos.x, y=datos.y,
            nivel_riesgo=nivel_riesgo,
            tipo_amenaza="GUSANO" if tiene_gusano else "Ninguna",
            frutos_disponibles=datos.frutos_disponibles,
            listo_para_cosechar=listo_cosecha,
            tiene_gusano=tiene_gusano
        )
        self.mapa_estados[(datos.x, datos.y)] = estado
        self.celdas_exploradas.add((datos.x, datos.y))
        
        # 4. Actualizar UI
        self._notificar_ui()

    def reportar_cosecha(self, cantidad: int):
        self.frutos_cosechados_total += cantidad
        self._notificar_ui()

    def _notificar_ui(self):
        if not self._callback_ui: return
        
        # Preparar datos visuales de los agentes
        estados_agentes = []
        for agente in self.agentes_fisicos:
            # Obtener posición actual del objeto agente
            pos = agente.posicion_actual
            orden = self.controles_agentes[agente.agente_id]['orden_texto']
            
            vis = EstadoAgenteVisibilidad(
                id=agente.agente_id,
                x=pos[0], y=pos[1],
                orden_actual=orden,
                bateria=agente.bateria,
                cargando_frutos=agente.frutos_cargados
            )
            estados_agentes.append(vis)

        metricas = MetricasSistema(
            tiempo_transcurrido=time.time() - self.tiempo_inicio,
            celdas_exploradas=len(self.celdas_exploradas),
            celdas_totales=self.grid_filas * self.grid_columnas,
            frutos_cosechados=self.frutos_cosechados_total,
            agentes_activos=len(self.agentes_fisicos),
            amenazas_gusano=self.contador_gusanos
        )
        
        self._callback_ui(list(self.mapa_estados.values()), estados_agentes, metricas)

    def detener_todo(self):
        for id_a in self.controles_agentes:
            self.emitir_orden(id_a, OrdenCapataz.ABANDONAR)