# -*- coding: utf-8 -*-
"""
AGENTE CAPATAZ - SUPERVISOR DE RECOLECTORES
============================================

Responsabilidades:
1. Supervisar a los 3 recolectores autonomos
2. Observar el estado del huerto desde posicion fija
3. Emitir ordenes: PARATE, CONTINUA, ABANDONA
4. Tomar decisiones basadas en:
   - Estado de los agentes
   - Nivel de contaminacion por gusanos
   - Eficiencia de recoleccion
   - Bateria de los agentes
"""

import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import Lock


# TIPOS DE ORDENES DEL CAPATAZ

class TipoOrden(Enum):
    """Ordenes que puede emitir el capataz"""
    PARATE = "PARATE"           # Detiene al recolector
    CONTINUA = "CONTINUA"       # Reanuda la recoleccion
    ABANDONA = "ABANDONA"       # Abandona completamente la recoleccion


@dataclass
class OrdenCapataz:
    """Orden emitida por el capataz a un recolector"""
    agente_destino: int
    tipo_orden: TipoOrden
    razon: str
    prioridad: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __str__(self):
        return f"[Orden para Agente {self.agente_destino}] {self.tipo_orden.value}: {self.razon}"


# RAZONES PARA EMITIR ORDENES

class RazonOrden(Enum):
    """Razones por las que el capataz emite ordenes"""
    # PARATE
    BATERIA_BAJA = "Bateria baja - necesita recarga"
    ZONA_CONTAMINADA = "Zona altamente contaminada por gusanos"
    SOBRECARGA = "Capacidad de carga completa"
    MANTENIMIENTO = "Requiere mantenimiento"
    
    # CONTINUA
    BATERIA_RECUPERADA = "Bateria restaurada"
    ZONA_SEGURA = "Zona libre de contaminacion"
    CAPACIDAD_DISPONIBLE = "Capacidad de carga disponible"
    
    # ABANDONA
    EMERGENCIA = "Situacion de emergencia"
    CONTAMINACION_CRITICA = "Contaminacion critica en el huerto"
    FIN_TURNO = "Fin de turno de trabajo"
    EFICIENCIA_BAJA = "Eficiencia muy baja"


@dataclass
class EstadoAgente:
    """Estado actual de un agente recolector"""
    agente_id: int
    posicion: Tuple[int, int]
    bateria: float
    frutos_cargados: int
    estado: str  # 'recolectando', 'parado', 'abandonado'
    celdas_exploradas: int
    cosechas_completadas: int
    eficiencia: float  # frutos por minuto
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# AGENTE CAPATAZ

class AgenteCapataz:
    """
    Agente Capataz: Supervisor del sistema de recoleccion
    
    Caracteristicas:
    - Posicion fija observando el huerto
    - Monitorea estado de todos los recolectores
    - Emite ordenes basadas en reglas y condiciones
    - Toma decisiones para optimizar la recoleccion
    - Previene situaciones de riesgo
    """
    
    def __init__(
        self, 
        posicion_observacion: Tuple[int, int] = (0, 0),
        num_agentes: int = 3
    ):
        """
        Inicializa el Agente Capataz
        
        Args:
            posicion_observacion: Posicion fija desde donde observa
            num_agentes: Número de recolectores a supervisar
        """
        self.posicion = posicion_observacion
        self.num_agentes = num_agentes
        
        # Estado de los agentes supervisados
        self.estados_agentes: Dict[int, EstadoAgente] = {}
        
        # Historial de ordenes emitidas
        self.ordenes_emitidas: List[OrdenCapataz] = []
        
        # Estadisticas del capataz
        self.ordenes_parate = 0
        self.ordenes_continua = 0
        self.ordenes_abandona = 0
        self.decisiones_totales = 0
        
        # Control
        self.activo = True
        self.lock = Lock()
        
        # Umbrales de decision
        self.umbrales = {
            'bateria_baja': 15.0,
            'bateria_critica': 5.0,
            'contaminacion_alta': 7.0,
            'contaminacion_critica': 9.0,
            'capacidad_llena': 0.9,  # 90% de capacidad
            'eficiencia_minima': 5.0,  # frutos por minuto
        }
        
        # Tiempo de inicio
        self.tiempo_inicio = time.time()
        
        print(f"\n{'='*70}")
        print(f"[CAPATAZ] AGENTE CAPATAZ INICIALIZADO")
        print(f"{'='*70}")
        print(f"[POSICION] Posicion de observacion: {posicion_observacion}")
        print(f"[EQUIPO] Supervisando {num_agentes} recolectores")
        print(f"[OBJETIVO] Listo para emitir ordenes: PARATE, CONTINUA, ABANDONA")
        print(f"{'='*70}\n")
    
    # ========================================================================
    # RECEPCION DE ESTADOS (DESDE LOS AGENTES)
    # ========================================================================
    
    def actualizar_estado_agente(
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
        Recibe actualizacion de estado de un agente
        
        Args:
            agente_id: ID del agente
            posicion: Posicion actual (x, y)
            bateria: Nivel de bateria (0-100)
            frutos_cargados: Cantidad de frutos en carga
            estado: 'recolectando', 'parado', 'abandonado'
            celdas_exploradas: Total de celdas exploradas
            cosechas_completadas: Total de cosechas realizadas
        """
        # Calcular eficiencia
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        eficiencia = (cosechas_completadas / (tiempo_transcurrido / 60)) if tiempo_transcurrido > 0 else 0
        
        # Actualizar estado
        estado_agente = EstadoAgente(
            agente_id=agente_id,
            posicion=posicion,
            bateria=bateria,
            frutos_cargados=frutos_cargados,
            estado=estado,
            celdas_exploradas=celdas_exploradas,
            cosechas_completadas=cosechas_completadas,
            eficiencia=eficiencia
        )
        
        with self.lock:
            self.estados_agentes[agente_id] = estado_agente
        
        # Evaluar si necesita emitir una orden
        self._evaluar_y_emitir_orden(agente_id)
    
    def reportar_contaminacion(self, celda: Tuple[int, int], nivel: float):
        """
        Recibe reporte de contaminacion por gusanos
        
        Args:
            celda: Coordenadas de la celda contaminada
            nivel: Nivel de contaminacion (0-10)
        """
        if nivel >= self.umbrales['contaminacion_critica']:
            print(f"[Capataz] [ADVERTENCIA] ALERTA: Contaminacion critica en {celda} (Nivel: {nivel:.1f})")
            self._emitir_ordenes_emergencia_contaminacion(celda)
        
        elif nivel >= self.umbrales['contaminacion_alta']:
            print(f"[Capataz] [ADVERTENCIA] Contaminacion alta en {celda} (Nivel: {nivel:.1f})")
            self._evaluar_agentes_cercanos(celda)
    
    # ========================================================================
    # LOGICA DE DECISION
    # ========================================================================
    
    def _evaluar_y_emitir_orden(self, agente_id: int):
        """
        Evalúa el estado de un agente y decide si emitir una orden
        
        Proceso de decision:
        1. Verificar bateria
        2. Verificar capacidad de carga
        3. Verificar eficiencia
        4. Verificar estado actual
        5. Emitir orden si es necesario
        """
        estado = self.estados_agentes.get(agente_id)
        if not estado:
            return
        
        # REGLA 1: Bateria critica → ABANDONA
        if estado.bateria <= self.umbrales['bateria_critica']:
            self._emitir_orden(
                agente_id,
                TipoOrden.ABANDONA,
                RazonOrden.EMERGENCIA.value + f" (Bateria: {estado.bateria:.1f}%)",
                prioridad=5
            )
            return
        
        # REGLA 2: Bateria baja → PARATE
        if estado.bateria <= self.umbrales['bateria_baja'] and estado.estado == 'recolectando':
            self._emitir_orden(
                agente_id,
                TipoOrden.PARATE,
                RazonOrden.BATERIA_BAJA.value + f" ({estado.bateria:.1f}%)",
                prioridad=4
            )
            return
        
        # REGLA 3: Bateria recuperada → CONTINUA
        if estado.bateria > 50.0 and estado.estado == 'parado':
            # Verificar que se detuvo por bateria baja
            ultima_orden = self._obtener_ultima_orden(agente_id)
            if ultima_orden and ultima_orden.tipo_orden == TipoOrden.PARATE:
                self._emitir_orden(
                    agente_id,
                    TipoOrden.CONTINUA,
                    RazonOrden.BATERIA_RECUPERADA.value + f" ({estado.bateria:.1f}%)",
                    prioridad=3
                )
                return
        
        # REGLA 4: Capacidad llena → PARATE
        capacidad_maxima = 50  # Ajustar según configuracion real
        porcentaje_carga = estado.frutos_cargados / capacidad_maxima
        
        if porcentaje_carga >= self.umbrales['capacidad_llena'] and estado.estado == 'recolectando':
            self._emitir_orden(
                agente_id,
                TipoOrden.PARATE,
                RazonOrden.SOBRECARGA.value + f" ({estado.frutos_cargados}/{capacidad_maxima})",
                prioridad=3
            )
            return
        
        # REGLA 5: Eficiencia baja → Advertencia (y eventualmente ABANDONA)
        if estado.eficiencia < self.umbrales['eficiencia_minima'] and estado.celdas_exploradas > 20:
            print(f"[Capataz] [DATOS] Agente {agente_id}: Eficiencia baja ({estado.eficiencia:.1f} frutos/min)")
            
            # Si la eficiencia es MUY baja, abandonar
            if estado.eficiencia < 2.0:
                self._emitir_orden(
                    agente_id,
                    TipoOrden.ABANDONA,
                    RazonOrden.EFICIENCIA_BAJA.value + f" ({estado.eficiencia:.1f} frutos/min)",
                    prioridad=2
                )
    
    def _evaluar_agentes_cercanos(self, celda_contaminada: Tuple[int, int]):
        """
        Evalúa agentes cercanos a una zona contaminada
        
        Args:
            celda_contaminada: Coordenadas de la celda con alta contaminacion
        """
        for agente_id, estado in self.estados_agentes.items():
            # Calcular distancia Manhattan
            distancia = abs(estado.posicion[0] - celda_contaminada[0]) + \
                       abs(estado.posicion[1] - celda_contaminada[1])
            
            # Si esta muy cerca y recolectando, detenerlo
            if distancia <= 2 and estado.estado == 'recolectando':
                self._emitir_orden(
                    agente_id,
                    TipoOrden.PARATE,
                    RazonOrden.ZONA_CONTAMINADA.value + f" (Distancia: {distancia} celdas)",
                    prioridad=4
                )
    
    def _emitir_ordenes_emergencia_contaminacion(self, celda: Tuple[int, int]):
        """
        Emite ordenes de emergencia por contaminacion critica
        
        Args:
            celda: Coordenadas de la celda con contaminacion critica
        """
        print(f"\n[Capataz] [EMERGENCIA] EMERGENCIA: Emitiendo ordenes de abandono por contaminacion critica")
        
        for agente_id in self.estados_agentes.keys():
            self._emitir_orden(
                agente_id,
                TipoOrden.ABANDONA,
                RazonOrden.CONTAMINACION_CRITICA.value + f" en {celda}",
                prioridad=5
            )
    
    # ========================================================================
    # EMISION Y GESTION DE ORDENES
    # ========================================================================
    
    def _emitir_orden(
        self, 
        agente_id: int, 
        tipo_orden: TipoOrden, 
        razon: str,
        prioridad: int = 3
    ):
        """
        Emite una orden a un agente especifico
        
        Args:
            agente_id: ID del agente destinatario
            tipo_orden: PARATE, CONTINUA o ABANDONA
            razon: Razon de la orden
            prioridad: Nivel de prioridad (1-5)
        """
        orden = OrdenCapataz(
            agente_destino=agente_id,
            tipo_orden=tipo_orden,
            razon=razon,
            prioridad=prioridad
        )
        
        with self.lock:
            self.ordenes_emitidas.append(orden)
            self.decisiones_totales += 1
            
            if tipo_orden == TipoOrden.PARATE:
                self.ordenes_parate += 1
            elif tipo_orden == TipoOrden.CONTINUA:
                self.ordenes_continua += 1
            elif tipo_orden == TipoOrden.ABANDONA:
                self.ordenes_abandona += 1
        
        # Mostrar la orden
        print(f"\n[Capataz] [ANUNCIO] {orden}")
        print(f"[Capataz] Prioridad: {'[PRIORIDAD]' * prioridad}")
        
        # Aqui se enviaria la orden al agente
        # En la implementacion real, llamaria a un callback o metodo del agente
        return orden
    
    def _obtener_ultima_orden(self, agente_id: int) -> Optional[OrdenCapataz]:
        """Obtiene la última orden emitida a un agente"""
        ordenes_agente = [o for o in self.ordenes_emitidas if o.agente_destino == agente_id]
        return ordenes_agente[-1] if ordenes_agente else None
    
    # ========================================================================
    # ORDENES MANUALES (CONTROL DIRECTO)
    # ========================================================================
    
    def ordenar_parate(self, agente_id: int, razon: str = "Orden manual del capataz"):
        """Orden manual: PARATE"""
        self._emitir_orden(agente_id, TipoOrden.PARATE, razon, prioridad=5)
    
    def ordenar_continua(self, agente_id: int, razon: str = "Orden manual del capataz"):
        """Orden manual: CONTINUA"""
        self._emitir_orden(agente_id, TipoOrden.CONTINUA, razon, prioridad=5)
    
    def ordenar_abandona(self, agente_id: int, razon: str = "Orden manual del capataz"):
        """Orden manual: ABANDONA"""
        self._emitir_orden(agente_id, TipoOrden.ABANDONA, razon, prioridad=5)
    
    def ordenar_fin_turno(self):
        """Ordena a todos los agentes abandonar (fin de turno)"""
        print(f"\n[Capataz] [CAMPANA] FIN DE TURNO - Ordenando abandono general")
        
        for agente_id in self.estados_agentes.keys():
            self._emitir_orden(
                agente_id,
                TipoOrden.ABANDONA,
                RazonOrden.FIN_TURNO.value,
                prioridad=5
            )
    
    # ========================================================================
    # MONITOREO Y REPORTES
    # ========================================================================
    
    def mostrar_estado_supervision(self):
        """Muestra el estado actual de la supervision"""
        print(f"\n{'='*70}")
        print(f"[CAPATAZ] ESTADO DE SUPERVISION - CAPATAZ")
        print(f"{'='*70}")
        print(f"[POSICION] Posicion: {self.posicion}")
        print(f"[EQUIPO] Agentes supervisados: {len(self.estados_agentes)}")
        print(f"\n[DATOS] ORDENES EMITIDAS:")
        print(f"  • PARATE: {self.ordenes_parate}")
        print(f"  • CONTINUA: {self.ordenes_continua}")
        print(f"  • ABANDONA: {self.ordenes_abandona}")
        print(f"  • Total decisiones: {self.decisiones_totales}")
        
        print(f"\n👷 ESTADO DE AGENTES:")
        for agente_id, estado in sorted(self.estados_agentes.items()):
            icono = {
                'recolectando': '[OK]',
                'parado': '[PAUSA]',
                'abandonado': '[DETENER]'
            }.get(estado.estado, '❓')
            
            print(f"  {icono} Agente {agente_id}:")
            print(f"     Posicion: {estado.posicion}")
            print(f"     Estado: {estado.estado}")
            print(f"     Bateria: {estado.bateria:.1f}%")
            print(f"     Frutos: {estado.frutos_cargados}")
            print(f"     Eficiencia: {estado.eficiencia:.1f} frutos/min")
        
        print(f"{'='*70}\n")
    
    def generar_reporte_final(self) -> str:
        """Genera un reporte final de la supervision"""
        tiempo_total = time.time() - self.tiempo_inicio
        mins = int(tiempo_total // 60)
        segs = int(tiempo_total % 60)
        
        reporte = f"""
{'='*70}
[INFO] REPORTE FINAL DEL CAPATAZ
{'='*70}

[TIEMPO]  TIEMPO DE SUPERVISION: {mins:02d}:{segs:02d}

[ANUNCIO] ORDENES EMITIDAS:
  • PARATE: {self.ordenes_parate} ordenes
  • CONTINUA: {self.ordenes_continua} ordenes
  • ABANDONA: {self.ordenes_abandona} ordenes
  • Total decisiones: {self.decisiones_totales}

[EQUIPO] AGENTES SUPERVISADOS: {len(self.estados_agentes)}

[DATOS] RENDIMIENTO PROMEDIO:
"""
        
        if self.estados_agentes:
            eficiencia_promedio = sum(e.eficiencia for e in self.estados_agentes.values()) / len(self.estados_agentes)
            bateria_promedio = sum(e.bateria for e in self.estados_agentes.values()) / len(self.estados_agentes)
            cosechas_totales = sum(e.cosechas_completadas for e in self.estados_agentes.values())
            
            reporte += f"""  • Eficiencia promedio: {eficiencia_promedio:.1f} frutos/min
  • Bateria promedio final: {bateria_promedio:.1f}%
  • Cosechas totales: {cosechas_totales}
"""
        
        reporte += f"\n{'='*70}\n"
        
        return reporte
    
    def detener(self):
        """Detiene el capataz"""
        self.activo = False
        print(f"[Capataz] [DETENER] Supervision finalizada")


# ========================================================================
# EJEMPLO DE USO
# ========================================================================

if __name__ == "__main__":
    print("\n[PRUEBA] DEMO: AGENTE CAPATAZ\n")
    
    # Crear capataz
    capataz = AgenteCapataz(posicion_observacion=(0, 0), num_agentes=3)
    
    # Simular actualizaciones de estado
    print("\n[COMUNICACION] Simulando actualizaciones de agentes...\n")
    
    # Agente 1: Bateria baja
    capataz.actualizar_estado_agente(
        agente_id=1,
        posicion=(3, 4),
        bateria=12.0,  # Bateria baja
        frutos_cargados=15,
        estado='recolectando',
        celdas_exploradas=25,
        cosechas_completadas=3
    )
    
    time.sleep(1)
    
    # Agente 2: Normal
    capataz.actualizar_estado_agente(
        agente_id=2,
        posicion=(5, 5),
        bateria=75.0,
        frutos_cargados=20,
        estado='recolectando',
        celdas_exploradas=30,
        cosechas_completadas=5
    )
    
    time.sleep(1)
    
    # Agente 3: Capacidad llena
    capataz.actualizar_estado_agente(
        agente_id=3,
        posicion=(7, 2),
        bateria=60.0,
        frutos_cargados=48,  # Casi lleno
        estado='recolectando',
        celdas_exploradas=28,
        cosechas_completadas=4
    )
    
    time.sleep(1)
    
    # Reporte de contaminacion
    print("\n")
    capataz.reportar_contaminacion(celda=(3, 5), nivel=8.5)
    
    time.sleep(1)
    
    # Mostrar estado
    capataz.mostrar_estado_supervision()
    
    # Orden manual
    print("\n[ANUNCIO] Orden manual del capataz:\n")
    capataz.ordenar_continua(1, "Bateria suficientemente recargada")
    
    time.sleep(1)
    
    # Fin de turno
    print("\n")
    capataz.ordenar_fin_turno()
    
    # Reporte final
    print(capataz.generar_reporte_final())