"""
MAIN
====
Punto de entrada.
"""
import time
from threading import Thread
from manager import AgenteCapataz, OrdenCapataz
from ui import AgenteUI

def main():
    # 1. Inicializar Capataz y UI
    capataz = AgenteCapataz(grid_filas=10, grid_columnas=10, num_agentes=3)
    ui = AgenteUI(grid_filas=10, grid_columnas=10)
    
    # 2. Conectar
    capataz.registrar_agente_ui(ui.actualizar)
    capataz.crear_agentes_fisicos()
    capataz.distribuir_trabajo()
    
    # 3. Iniciar lógica de agentes en segundo plano
    threads_agentes = capataz.iniciar_jornada()
    
    # 4. Iniciar UI en hilo principal (necesario para Pygame)
    #    Simulamos eventos de teclado para probar al Capataz manualmente también
    
    print("\n CONTROLES DE TECLADO (SIMULACIÓN CAPATAZ MANUAL):")
    print(" [ESPACIO]: Parar a todos los agentes")
    print(" [ENTER]:   Reanudar a todos los agentes")
    print(" [ESC]:     Salir")
    
    # Inyectamos lógica de teclado en el loop de UI para demo
    import pygame
    
    # Modificamos el loop de UI ligeramente para manejar teclas globales aquí
    ui.inicializar_pygame()
    
    while ui.running:
        # Eventos UI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ui.running = False
            
            # --- INTERACCIÓN MANUAL CON EL CAPATAZ ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("USER INPUT: PARAR TODOS")
                    for id_a in capataz.controles_agentes:
                        capataz.emitir_orden(id_a, OrdenCapataz.PARAR)
                        
                elif event.key == pygame.K_RETURN:
                    print("USER INPUT: CONTINUAR TODOS")
                    for id_a in capataz.controles_agentes:
                        capataz.emitir_orden(id_a, OrdenCapataz.CONTINUAR)
        
        # Renderizado
        ui.screen.fill((30,30,30))
        ui._dibujar_capataz()
        ui._dibujar_grid()
        ui._dibujar_agentes()
        ui._dibujar_panel()
        pygame.display.flip()
        ui.clock.tick(30)
        
        # Verificar si todos terminaron
        if all(not t.is_alive() for t in threads_agentes):
            print("Todos los agentes han regresado.")
            # No cerramos automático para poder ver el resultado final

    # Limpieza
    capataz.detener_todo()
    pygame.quit()

if __name__ == "__main__":
    main()