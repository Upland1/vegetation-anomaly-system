"""
SISTEMA MULTI-AGENTE - PUNTO DE ENTRADA PRINCIPAL
==================================================

Este script coordina todo el sistema:
1. Inicializa el Agente Manager
2. Crea los Agentes Físicos
3. Inicia el Agente UI con Pygame
4. Ejecuta la simulación completa
5. Muestra resumen final

INSTRUCCIONES DE USO:
--------------------
1. Asegúrate de tener pygame instalado:
   pip install pygame

2. Coloca estos archivos en la misma carpeta:
   - main.py (este archivo)
   - manager.py
   - fisico.py
   - ui.py

3. Ejecuta:
   python main.py

4. Para personalizar la simulación, edita las constantes al inicio del archivo
"""

import time
import sys
from threading import Thread

# Importar los tres agentes
from manager import AgenteManager
from fisico import AgenteFisico
from ui import AgenteUI


# CONFIGURACIÓN DE LA SIMULACIÓN

class ConfiguracionSimulacion:
    """Parámetros configurables de la simulación"""
    
    # Dimensiones del cultivo
    GRID_FILAS = 10
    GRID_COLUMNAS = 10
    
    # Número de agentes físicos trabajando en paralelo
    NUM_AGENTES = 5
    
    # Velocidad de la simulación (factor de aceleración)
    # 1.0 = tiempo real, 0.5 = mitad de velocidad, 2.0 = doble velocidad
    VELOCIDAD_SIMULACION = 0.5
    
    # Mostrar logs detallados
    VERBOSE = True


# SISTEMA PRINCIPAL

class SistemaMultiAgente:
    """
    Orquestador del sistema completo
    
    Coordina la interacción entre:
    - Agente Manager (cerebro del sistema)
    - Agentes Físicos (ejecutores)
    - Agente UI (visualización)
    """
    
    def __init__(self, config: ConfiguracionSimulacion):
        self.config = config
        
        # Los tres agentes principales
        self.manager = None
        self.ui = None
        
        # Control
        self.sistema_activo = False
        
        print("\n" + "="*80)
        print("🚀 SISTEMA MULTI-AGENTE DE MONITOREO DE CULTIVO".center(80))
        print("="*80 + "\n")
    
    def inicializar(self):
        """Inicializa todos los componentes del sistema"""
        print("📋 Fase 1: Inicializando componentes...\n")
        
        # 1. CREAR AGENTE MANAGER
        print("🧠 Creando Agente Manager...")
        self.manager = AgenteManager(
            grid_filas=self.config.GRID_FILAS,
            grid_columnas=self.config.GRID_COLUMNAS,
            num_agentes=self.config.NUM_AGENTES
        )
        print("   ✅ Manager creado\n")
        
        # 2. CREAR AGENTE UI
        print("🖥️  Creando Agente UI...")
        self.ui = AgenteUI(
            grid_filas=self.config.GRID_FILAS,
            grid_columnas=self.config.GRID_COLUMNAS
        )
        print("   ✅ UI creado\n")
        
        # 3. CONECTAR MANAGER CON UI
        print("🔗 Conectando Manager <-> UI...")
        self.manager.registrar_agente_ui(self.ui.actualizar)
        print("   ✅ Conexión establecida\n")
        
        # 4. CREAR AGENTES FÍSICOS
        print("🤖 Creando Agentes Físicos...")
        self.manager.crear_agentes_fisicos()
        
        # Conectar agentes con UI para tracking de posiciones
        for agente in self.manager.agentes_fisicos:
            # Sobrescribir método _mover_a para notificar a UI
            original_mover = agente._mover_a
            
            def mover_con_ui(celda, agente_id=agente.agente_id):
                original_mover(celda)
                self.ui.actualizar_posicion_agente(agente_id, celda[0], celda[1])
            
            agente._mover_a = mover_con_ui
        
        print("   ✅ Todos los agentes creados\n")
        
        # 5. DISTRIBUIR TRABAJO
        print("📦 Distribuyendo trabajo entre agentes...")
        self.manager.distribuir_trabajo()
        print("   ✅ Trabajo distribuido\n")
        
        print("="*80)
        print("✅ SISTEMA INICIALIZADO CORRECTAMENTE".center(80))
        print("="*80 + "\n")
        
        self.sistema_activo = True
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación completa"""
        if not self.sistema_activo:
            print("⚠️  Error: Sistema no inicializado. Llama inicializar() primero.")
            return
        
        print("\n" + "="*80)
        print("🎬 INICIANDO SIMULACIÓN".center(80))
        print("="*80 + "\n")
        
        # Iniciar Pygame en el thread principal
        print("🖥️  Iniciando visualización Pygame...")
        self.ui.inicializar_pygame()
        print("   ✅ Pygame iniciado\n")
        
        # Mensaje de inicio
        print("🌾 Los agentes comenzarán a explorar el cultivo...")
        print("📊 La visualización se actualizará en tiempo real")
        print("💡 Presiona ESC en la ventana de Pygame para salir\n")
        print("-"*80 + "\n")
        
        # Ejecutar exploración multi-agente en threads separados
        try:
            # Iniciar exploración en threads
            exploracion_thread = Thread(target=self.manager.iniciar_exploracion_multi_agente, daemon=True)
            exploracion_thread.start()
            
            # Ejecutar loop de Pygame en el thread principal
            self.ui.ejecutar_loop_pygame()
            
            # Esperar a que termine la exploración
            exploracion_thread.join(timeout=1)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulación interrumpida por el usuario")
            self.detener()
            return
        
        # Esperar un momento antes de mostrar resumen
        print("\n" + "="*80)
        print("⏸️  Esperando 3 segundos para visualizar resultados...".center(80))
        print("="*80 + "\n")
        time.sleep(3)
    
    def mostrar_resumen(self):
        """Muestra el resumen final del sistema"""
        print("\n" + "="*80)
        print("📋 GENERANDO REPORTE FINAL".center(80))
        print("="*80 + "\n")
        
        # Reporte del Manager
        reporte_manager = self.manager.generar_reporte()
        print(reporte_manager)
        
        # Resumen visual de UI
        if self.ui:
            self.ui.mostrar_resumen_final()
    
    def detener(self):
        """Detiene el sistema de forma ordenada"""
        print("\n🛑 Deteniendo sistema...")
        
        # Detener agentes físicos
        if self.manager:
            for agente in self.manager.agentes_fisicos:
                agente.detener()
        
        # Detener UI
        if self.ui:
            self.ui.detener()
        
        print("✅ Sistema detenido\n")
    
    def ejecutar_completo(self):
        """Ejecuta el ciclo completo: inicializar -> simular -> reportar"""
        try:
            # Fase 1: Inicialización
            self.inicializar()
            
            # Pequeña pausa antes de comenzar
            print("⏳ Iniciando en 3 segundos...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print()
            
            # Fase 2: Simulación
            self.ejecutar_simulacion()
            
            # Fase 3: Resumen
            self.mostrar_resumen()
            
        except Exception as e:
            print(f"\n❌ Error en la simulación: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.detener()


# PUNTO DE ENTRADA

def main():
    """Función principal"""
    # Banner inicial
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "   SISTEMA MULTI-AGENTE DE MONITOREO Y GESTIÓN DE CULTIVOS".center(78) + "║")
    print("║" + " "*78 + "║")
    print("║" + f"   Grid: {ConfiguracionSimulacion.GRID_FILAS}x{ConfiguracionSimulacion.GRID_COLUMNAS}".ljust(78) + "║")
    print("║" + f"   Agentes: {ConfiguracionSimulacion.NUM_AGENTES}".ljust(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Crear configuración
    config = ConfiguracionSimulacion()
    
    # Crear y ejecutar sistema
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()
    
    # Mensaje de despedida
    print("\n" + "="*80)
    print("👋 GRACIAS POR USAR EL SISTEMA".center(80))
    print("="*80 + "\n")


# MODO DE PRUEBA RÁPIDA

def modo_prueba_rapida():
    """
    Modo de prueba con configuración reducida para debugging
    """
    print("\n🧪 MODO DE PRUEBA RÁPIDA\n")
    
    # Configuración reducida
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 5
    config.GRID_COLUMNAS = 5
    config.NUM_AGENTES = 2
    config.VELOCIDAD_SIMULACION = 0.3
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


# EJEMPLOS DE USO AVANZADO

def ejemplo_cultivo_pequeno():
    """Ejemplo: Cultivo pequeño con 2 agentes"""
    print("\n🌱 EJEMPLO: Cultivo Pequeño (5x5, 2 agentes)\n")
    
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 5
    config.GRID_COLUMNAS = 5
    config.NUM_AGENTES = 2
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


def ejemplo_cultivo_grande():
    """Ejemplo: Cultivo grande con muchos agentes"""
    print("\n🌳 EJEMPLO: Cultivo Grande (15x15, 8 agentes)\n")
    
    config = ConfiguracionSimulacion()
    config.GRID_FILAS = 15
    config.GRID_COLUMNAS = 15
    config.NUM_AGENTES = 8
    
    sistema = SistemaMultiAgente(config)
    sistema.ejecutar_completo()


def ejemplo_monitoreo_solo():
    """Ejemplo: Solo monitoreo sin cosecha"""
    print("\n👁️  EJEMPLO: Modo Monitoreo (sin cosecha)\n")
    
    config = ConfiguracionSimulacion()
    sistema = SistemaMultiAgente(config)
    sistema.inicializar()
    
    # Deshabilitar cosecha
    for agente in sistema.manager.agentes_fisicos:
        agente.config.velocidad_cosecha = 0.0
    
    sistema.ejecutar_simulacion()
    sistema.mostrar_resumen()
    sistema.detener()


# EJECUCIÓN

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pygame
    except ImportError:
        print("\n❌ ERROR: Pygame no está instalado")
        print("📦 Instálalo con: pip install pygame\n")
        sys.exit(1)
    
    # Verificar archivos necesarios
    import os
    archivos_requeridos = ['manager.py', 'fisico.py', 'ui.py']
    archivos_faltantes = [f for f in archivos_requeridos if not os.path.exists(f)]
    
    if archivos_faltantes:
        print("\n❌ ERROR: Faltan archivos necesarios:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print("\n📋 Asegúrate de tener todos los archivos en la misma carpeta\n")
        sys.exit(1)
    
    # EJECUTAR MODO PRINCIPAL
    main()
    
    # DESCOMENTAR PARA OTROS MODOS:
    # modo_prueba_rapida()
    # ejemplo_cultivo_pequeno()
    # ejemplo_cultivo_grande()
    # ejemplo_monitoreo_solo()