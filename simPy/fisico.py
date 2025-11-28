"""
AGENTE FÍSICO
=============
Recolectores autónomos que escuchan las órdenes del Capataz.
"""

import time
import random
from typing import List, Tuple, Callable
from manager import DatosExploracion, OrdenCapataz

class AgenteFisico:
    def __init__(self, agente_id: int, callback_datos: Callable, callback_cosecha: Callable, control_evento, control_abortar):
        self.agente_id = agente_id
        
        # Callbacks y Controles del Capataz
        self.cb_datos = callback_datos
        self.cb_cosecha = callback_cosecha
        self.evento_pausa = control_evento   # threading.Event
        self.check_abortar = control_abortar # lambda function
        
        # Estado físico
        self.posicion_actual = (0, 0)
        self.celdas_asignadas = []
        self.bateria = 100.0
        self.frutos_cargados = 0
        self.activo = True

    def asignar_celdas(self, celdas: List[Tuple[int, int]]):
        self.celdas_asignadas = celdas

    def iniciar_trabajo(self):
        """Bucle principal de trabajo"""
        print(f"[Agente {self.agente_id}] 🚜 Arrancando motores.")
        
        for celda in self.celdas_asignadas:
            if not self.activo: break
            
            # --- PUNTO DE CONTROL DEL CAPATAZ (Antes de moverse) ---
            if not self._verificar_ordenes_capataz(): 
                break # Si retorna False, es que hubo orden de ABANDONAR
            
            # 1. Moverse
            self._mover_a(celda)
            
            # --- PUNTO DE CONTROL (Al llegar) ---
            if not self._verificar_ordenes_capataz(): break
            
            # 2. Explorar y trabajar
            self._procesar_celda(celda)
            
            # Simular descarga si está lleno
            if self.frutos_cargados >= 20:
                self._ir_a_base_descargar()

        print(f"[Agente {self.agente_id}] 🏁 Turno finalizado.")

    def _verificar_ordenes_capataz(self) -> bool:
        """
        Consulta las señales del Capataz.
        Retorna True si puede continuar, False si debe abortar.
        """
        # 1. Revisar si hay orden de PARAR (wait bloqueará el hilo si está en clear)
        self.evento_pausa.wait() 
        
        # 2. Revisar si hay orden de ABANDONAR
        if self.check_abortar():
            print(f"[Agente {self.agente_id}] 🚨 ¡Orden de ABANDONAR recibida! Regresando a base...")
            self.posicion_actual = (0, 0) # Teletransporte de emergencia a base
            self.activo = False
            return False
            
        return True

    def _mover_a(self, celda):
        """Simula movimiento con retardo"""
        # Distancia Manhattan simple
        dist = abs(celda[0] - self.posicion_actual[0]) + abs(celda[1] - self.posicion_actual[1])
        # Tiempo de viaje
        time.sleep(dist * 0.1) 
        self.posicion_actual = celda
        self.bateria -= 0.1 * dist

    def _procesar_celda(self, celda):
        """Simula sensores y recolección"""
        # Simulación de datos aleatorios
        plagas = random.uniform(0, 10)
        # Probabilidad baja de GUSANO (plaga > 8)
        if random.random() < 0.05: 
            plagas = 9.5 
        
        maduracion = random.uniform(0, 10)
        frutos = random.randint(0, 5) if maduracion > 4 else 0
        
        datos = DatosExploracion(
            x=celda[0], y=celda[1],
            temperatura=25.0, humedad=60.0,
            nivel_plagas=plagas,
            nivel_nutrientes=5.0,
            nivel_maduracion=maduracion,
            frutos_disponibles=frutos,
            agente_id=self.agente_id
        )
        
        # Enviar al Capataz
        self.cb_datos(datos)
        
        # Lógica autónoma de cosecha (si el Capataz no ha gritado ABANDONA tras ver los datos)
        if plagas < 8.0 and frutos > 0 and maduracion > 7.0:
            self._cosechar(frutos)

    def _cosechar(self, cantidad):
        """Acción física de cosechar"""
        # Verificamos orden antes de empezar la tarea pesada
        if not self._verificar_ordenes_capataz(): return

        time.sleep(0.5) # Tiempo que tarda en cosechar
        self.frutos_cargados += cantidad
        self.cb_cosecha(cantidad)

    def _ir_a_base_descargar(self):
        print(f"[Agente {self.agente_id}] 📦 Descargando...")
        time.sleep(1)
        self.frutos_cargados = 0