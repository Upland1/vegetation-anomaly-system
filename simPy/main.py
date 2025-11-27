# -*- coding: utf-8 -*-
"""
SISTEMA MULTI-AGENTE - PUNTO DE ENTRADA PRINCIPAL
==================================================

Este script coordina todo el sistema:
1. Inicializa el Agente Manager
2. Crea los Agentes Fisicos
3. INTEGRA AL CAPATAZ como supervisor
4. Inicia el Agente UI con Pygame
5. Ejecuta la simulacion completa
6. Muestra resumen final

INSTRUCCIONES DE USO:
--------------------
1. Asegúrate de tener pygame instalado:
   pip install pygame

2. Coloca estos archivos en la misma carpeta:
   - main.py (este archivo)
   - manager.py
   - fisico.py
   - capataz.py  ← NUEVO
   - ui.py

3. Ejecuta:
   python main.py

4. Para personalizar la simulacion, edita las constantes al inicio del archivo
"""

import time
import sys
import os
from threading import Thread

# Configurar encoding UTF-8 para salida de consola
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Importar los agentes
from manager import AgenteManager
from fisico import AgenteFisico
from ui import AgenteUI
from capataz import AgenteCapataz


# CONFIGURACION DE LA SIMULACION

class ConfiguracionSimulacion:
    """Parametros configurables de la simulacion"""
    
    # Dimensiones del cultivo
    GRID_FILAS = 10
    GRID_COLUMNAS = 10
    
    # Número de agentes fisicos trabajando en paralelo
    NUM_AGENTES = 5
    
    # Velocidad de la simulacion (factor de aceleracion)
    # 1.0 = tiempo real, 0.5 = mitad de velocidad, 2.0 = doble velocidad
    VELOCIDAD_SIMULACION = 0.5
    
    # Mostrar logs detallados
    VERBOSE = True


# SISTEMA PRINCIPAL

class SistemaMultiAgente:
    """
    Orquestador del sistema completo
    
    Coordina la interaccion entre:
    - Agente Manager (cerebro del sistema)
    - Agentes Fisicos (ejecutores)
    - Agente Capataz (supervisor)
    - Agente UI (visualizacion)
    """
    
    def __init__(self, config: ConfiguracionSimulacion):
        self.config = config
        
        # Los agentes principales
        self.manager = None
        self.ui = None
        
        # Control
        self.sistema_activo = False
        
        print("\\n" + "="*80)
        print("[MENSAJE] SISTEMA MULTI-AGENTE DE MONITOREO DE CULTIVO".center(80))
        print("="*80 + "\\n")
    
    def inicializar(self):
        """Inicializa todos los componentes del sistema"""
        print("[INFO] Fase 1: Inicializando componentes...\n")
        
        # 1. CREAR AGENTE MANAGER
        print("[MANAGER] Creando Agente Manager...")
        self.manager = AgenteManager(
            grid_filas=self.config.GRID_FILAS,
            grid_columnas=self.config.GRID_COLUMNAS,
            num_agentes=self.config.NUM_AGENTES
        )
        print("   [OK] Manager creado\n")
        
        # 2. CREAR AGENTE UI
        print("[UI] Creando Agente UI...")
        self.ui = AgenteUI(
            grid_filas=self.config.GRID_FILAS,
            grid_columnas=self.config.GRID_COLUMNAS
        )
        
        # NUEVO: Registrar posicion del capataz en UI
        self.ui.posicion_capataz = self.manager.capataz.posicion
        
        print("   [OK] UI creado")
        print(f"   [CAPATAZ] Capataz registrado en posicion {self.ui.posicion_capataz}\n")
        
        # 3. CONECTAR MANAGER CON UI
        print("[CONEXION] Conectando Manager <-> UI...")
        self.manager.registrar_agente_ui(self.ui.actualizar)
        print("   [OK] Conexion establecida\n")
        
        # 4. CREAR AGENTES FISICOS (Ya incluye conexion con capataz)
        print("[AGENTES] Creando Agentes Fisicos...")
        self.manager.crear_agentes_fisicos()
        
        # Conectar agentes con UI para tracking de posiciones
        for agente in self.manager.agentes_fisicos:
            # Sobrescribir metodo _mover_a para notificar a UI
            original_mover = agente._mover_a
            
            def mover_con_ui(celda, agente_id=agente.agente_id):
                original_mover(celda)
                self.ui.actualizar_posicion_agente(agente_id, celda[0], celda[1])
            
            agente._mover_a = mover_con_ui
        
        # NUEVO: Conectar ordenes del capataz con agentes
        for agente in self.manager.agentes_fisicos:
            # Crear closure para capturar agente especifico
            def crear_callback_orden(agente_obj):
                def callback_orden(orden):
                    if orden.agente_destino == agente_obj.agente_id:
                        agente_obj.recibir_orden_capataz(orden.tipo_orden, orden.razon)
                return callback_orden
            
            # Registrar callback en el capataz
            # (El capataz llamara esto cuando emita ordenes)
            original_emitir = self.manager.capataz._emitir_orden
            
            def emitir_con_callback(agente_id, tipo_orden, razon, prioridad=3, capataz=self.manager.capataz):
                orden = original_emitir(agente_id, tipo_orden, razon, prioridad)
                # Enviar orden al agente correspondiente
                agente_obj = next((a for a in self.manager.agentes_fisicos if a.agente_id == agente_id), None)
                if agente_obj:
                    agente_obj.recibir_orden_capataz(orden.tipo_orden, orden.razon)
                return orden
            
            self.manager.capataz._emitir_orden = emitir_con_callback
        
        print("   [OK] Todos los agentes creados")
        print("   [CONEXION] Agentes conectados con el Capataz\n")
        
        # 5. DISTRIBUIR TRABAJO
        print("[TRABAJO] Distribuyendo trabajo entre agentes...")
        self.manager.distribuir_trabajo()
        print("   [OK] Trabajo distribuido\n")
        
        print("="*80)
        print("[OK] SISTEMA INICIALIZADO CORRECTAMENTE".center(80))
        print("="*80 + "\n")
        
        self.sistema_activo = True
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulacion completa"""
        if not self.sistema_activo:
            print("[ADVERTENCIA] Error: Sistema no inicializado. Llama inicializar() primero.")
            return
        
        print("\n" + "="*80)
        print("[SIMULACION] INICIANDO SIMULACION".center(80))
        print("="*80 + "\n")
        
        # Iniciar Pygame en el thread principal
        print("[UI] Iniciando visualizacion Pygame...")
        self.ui.inicializar_pygame()
        print("   [OK] Pygame iniciado\n")
        
        # Mensaje de inicio
        print("[CULTIVO] Los agentes comenzaran a explorar el cultivo...")
        print("[CAPATAZ] El Capataz supervisara desde la esquina superior izquierda")
        print("[DATOS] La visualizacion se actualizara en tiempo real")
        print("[TIP] Presiona ESC en la ventana de Pygame para salir\n")
        print("-"*80 + "\n")
        
        # Ejecutar exploracion multi-agente en threads separados
        try:
            # Iniciar exploracion en threads
            exploracion_thread = Thread(target=self.manager.iniciar_exploracion_multi_agente, daemon=True)
            exploracion_thread.start()
            
            # Ejecutar loop de Pygame en el thread principal
            self.ui.ejecutar_loop_pygame()
            
            # Esperar a que termine la exploracion
            exploracion_thread.join(timeout=1)
            
        except KeyboardInterrupt:
            print("\n\n[ADVERTENCIA] Simulacion interrumpida por el usuario")
            self.detener()
            return
        
        # Esperar un momento antes de mostrar resumen
        print("\n" + "="*80)
        print("[LINEA] Esperando 3 segundos para visualizar resultados...".center(80))
        print("="*80 + "\n")
        time.sleep(3)
    
    def mostrar_resumen(self):
        """Muestra el resumen final del sistema"""
        print("\n" + "="*80)
        print("[INFO] GENERANDO REPORTE FINAL".center(80))
        print("="*80 + "\n")
        
        # Reporte del Manager (incluye reporte del Capataz)
        reporte_manager = self.manager.generar_reporte()
        print(reporte_manager)
        
        # Mostrar estado final del Capataz
        self.manager.capataz.mostrar_estado_supervision()
        
        # Resumen visual de UI
        if self.ui:
            self.ui.mostrar_resumen_final()
    
    def detener(self):
        """Detiene el sistema de forma ordenada"""
        print("\n[DETENER] Deteniendo sistema...")
        
        # Detener agentes fisicos
        if self.manager:
            for agente in self.manager.agentes_fisicos:
                agente.detener()
        
        # Detener capataz
        if self.manager and self.manager.capataz:
            self.manager.capataz.detener()
        
        # Detener UI
        if self.ui:
            self.ui.detener()
        
        print("[OK] Sistema detenido\n")
    
    def ejecutar_completo(self):
        """Ejecuta el ciclo completo: inicializar -> simular -> reportar"""
        try:
            # Fase 1: Inicializacion
            self.inicializar()
            
            # Pequena pausa antes de comenzar
            print("[ESPERA] Iniciando en 3 segundos...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print()
            
            # Fase 2: Simulacion
            self.ejecutar_simulacion()
            
            # Fase 3: Resumen
            self.mostrar_resumen()
            
        except Exception as e:
            print(f"\n[ERROR] Error en la simulacion: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.detener()
    
    # ========================================================================
    # NUEVAS FUNCIONALIDADES: CONTROL MANUAL DEL CAPATAZ
    # ========================================================================
    
    def emitir_orden_manual_capataz(self, agente_id: int, tipo_orden: str, razon: str = "Orden manual"):
        """
        Permite emitir ordenes manuales del capataz durante la simulacion
        
        Args:
            agente_id: ID del agente (1-5)
            tipo_orden: 'PARATE', 'CONTINUA', 'ABANDONA'
            razon: Razon de la orden
        """
        if not self.manager or not self.manager.capataz:
            print("[ADVERTENCIA] Sistema no inicializado")
            return
        
        if tipo_orden == 'PARATE':
            self.manager.capataz.ordenar_parate(agente_id, razon)
        elif tipo_orden == 'CONTINUA':
            self.manager.capataz.ordenar_continua(agente_id, razon)
        elif tipo_orden == 'ABANDONA':
            self.manager.capataz.ordenar_abandona(agente_id, razon)
        else:
            print(f"[ADVERTENCIA] Orden desconocida: {tipo_orden}")
    
    def fin_turno_capataz(self):
        """Ordena fin de turno - todos los agentes abandonan"""
        if self.manager and self.manager.capataz:
            self.manager.capataz.ordenar_fin_turno()


# PUNTO DE ENTRADA

def main():
    """Funcion principal"""
    # Banner inicial
    print("\n")
    print("+" + "="*78 + "+")
    print("|" + " "*78 + "|")
    print("|" + "   SISTEMA MULTI-AGENTE DE MONITOREO Y GESTION DE CULTIVOS".center(78) + "|")
    print("|" + " "*78 + "|")
    print("|" + f"   Grid: {ConfiguracionSimulacion.GRID_FILAS}x{ConfiguracionSimulacion.GRID_COLUMNAS}".ljust(78) + "|")
    print("|" + f"   Agentes: {ConfiguracionSimulacion.NUM_AGENTES}".ljust(78) + "|")
    print("|" + f"   [CAPATAZ] Supervisando".ljust(78) + "|")
    print("|" + " "*78 + "|")
    print("+" + "="*78 + "+")
    print()
    
    # Crear configuracion
    config = ConfiguracionSimulacion()
    
    # Crear y ejecutar sistema
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()
    
    # Mensaje de despedida
    print("\n" + "="*80)
    print("[ADIOS] GRACIAS POR USAR EL SISTEMA".center(80))
    print("="*80 + "\n")


# MODO DE PRUEBA RAPIDA

def modo_prueba_rapida():
    """
    Modo de prueba con configuracion reducida para debugging
    """
    print("\n[PRUEBA] MODO DE PRUEBA RAPIDA\n")
    
    # Configuracion reducida
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 5
    config.GRID_COLUMNAS = 5
    config.NUM_AGENTES = 2
    config.VELOCIDAD_SIMULACION = 0.3
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


# EJEMPLOS DE USO AVANZADO

def ejemplo_cultivo_pequeno():
    """Ejemplo: Cultivo pequeno con 2 agentes"""
    print("\n[PEQUENO] EJEMPLO: Cultivo Pequeno (5x5, 2 agentes)\n")
    
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 5
    config.GRID_COLUMNAS = 5
    config.NUM_AGENTES = 2
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


def ejemplo_cultivo_grande():
    """Ejemplo: Cultivo grande con muchos agentes"""
    print("\n[GRANDE] EJEMPLO: Cultivo Grande (15x15, 8 agentes)\n")
    
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 15
    config.GRID_COLUMNAS = 15
    config.NUM_AGENTES = 8
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


def ejemplo_con_ordenes_capataz():
    """Ejemplo: Demostracion de ordenes manuales del capataz"""
    print("\n[CAPATAZ] EJEMPLO: Ordenes Manuales del Capataz\n")
    
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 8
    config.GRID_COLUMNAS = 8
    config.NUM_AGENTES = 3
    
    sistema = SistemaMultiAgente(config)
    sistema.inicializar()
    
    # Iniciar exploracion
    exploracion_thread = Thread(target=sistema.manager.iniciar_exploracion_multi_agente, daemon=True)
    exploracion_thread.start()
    
    # Esperar un poco
    time.sleep(5)
    
    # Emitir ordenes manuales
    print("\n[CAPATAZ] CAPATAZ EMITIENDO ORDENES MANUALES...\n")
    sistema.emitir_orden_manual_capataz(1, 'PARATE', 'Inspeccion de calidad')
    time.sleep(2)
    sistema.emitir_orden_manual_capataz(1, 'CONTINUA', 'Inspeccion completada')
    time.sleep(3)
    sistema.emitir_orden_manual_capataz(2, 'ABANDONA', 'Problema mecanico')
    
    # Esperar a que termine
    exploracion_thread.join()
    
    # Mostrar resumen
    sistema.mostrar_resumen()
    sistema.detener()


# EJECUCION

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pygame
    except ImportError:
        print("\n[ERROR] ERROR: Pygame no esta instalado")
        print("[TRABAJO] Instalalo con: pip install pygame\n")
        sys.exit(1)
    
    # Verificar archivos necesarios
    import os
    archivos_requeridos = ['manager.py', 'fisico.py', 'capataz.py', 'ui.py']
    archivos_faltantes = [f for f in archivos_requeridos if not os.path.exists(f)]
    
    if archivos_faltantes:
        print("\n[ERROR] ERROR: Faltan archivos necesarios:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print("\n[INFO] Asegúrate de tener todos los archivos en la misma carpeta\n")
        sys.exit(1)
    
    # EJECUTAR MODO PRINCIPAL
    main()
    
    # DESCOMENTAR PARA OTROS MODOS:
    # modo_prueba_rapida()
    # ejemplo_cultivo_pequeno()
    # ejemplo_cultivo_grande()
    # ejemplo_con_ordenes_capataz()