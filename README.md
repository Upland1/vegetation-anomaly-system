# 🍅 Sistema Multi-Agente de Monitoreo Agrícola

Este proyecto es una simulación de agricultura de precisión basada en sistemas multi-agente. Utiliza **Python** y **Pygame** para coordinar una flota de robots autónomos que exploran, analizan y cosechan un cultivo virtual en tiempo real.

## 📂 Estructura del Proyecto

El sistema está dividido en 4 módulos principales para desacoplar responsabilidades (Arquitectura Modular):

* **`main.py` (El Orquestador):** Punto de entrada. Inicializa el sistema, gestiona los hilos (threading) y sincroniza la lógica con la interfaz gráfica.
* **`manager.py` (El Cerebro):** Agente central que no tiene cuerpo físico. Recibe datos, toma decisiones estratégicas (riesgos, prioridad de cosecha) y asigna órdenes a los robots.
* **`fisico.py` (El Cuerpo):** Los robots que se mueven en el grid. Simulan sensores (temperatura, visión), actuadores (brazos robóticos) y gestionan su propia batería.
* **`ui.py` (Los Ojos):** Interfaz gráfica construida en Pygame. Visualiza el estado del grid y las métricas en tiempo real corriendo en el hilo principal.

## 🚀 Requisitos e Instalación

### 1. Prerrequisitos
Necesitas tener instalado **Python 3.x**.

### 2. Dependencias
El proyecto utiliza `pygame` para la visualización. Instálalo ejecutando:

```bash
pip install pygame
```

### 3. Organización de Archivos
Asegúrate de tener los 4 archivos de código en la misma carpeta:
* `main.py`
* `manager.py`
* `fisico.py`
* `ui.py`

## ▶️ Ejecución y Uso

Para iniciar la simulación, abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
python main.py
```

### 🎮 Durante la Simulación
* Se abrirá una ventana mostrando el mapa del cultivo.
* **Puntos de colores:** Son los agentes físicos moviéndose.
* **Celdas:**
    * 🌑 Gris: Desconocido.
    * 🟢 Verde: Sano / Bajo Riesgo.
    * 🔴 Rojo: Alto Riesgo / Plaga.
    * 🟣 Morado: Listo para cosechar.

### 🛑 FINALIZAR Y VER ESTADÍSTICAS (Importante)

El sistema genera un reporte detallado en la terminal al finalizar. Para verlo, debes terminar la ejecución gráfica correctamente:

1.  Espera a que los agentes terminen su exploración (se detendrán).
2.  **Opción A (Recomendada):** Presiona la tecla `ESC` en la ventana o cierra la ventana con la `X`.
3.  **Opción B (Forzada):** Ve a la terminal y presiona `Ctrl + C`.

> **⚠️ NOTA:** Al hacer esto, el hilo gráfico se cierra y el sistema imprimirá en tu consola el **Resumen Final de Rendimiento** (total cosechado, eficiencia, baterías, etc.). ¡No te pierdas este reporte!

## ⚙️ Personalización

Puedes modificar los parámetros de la simulación editando la clase `ConfiguracionSimulacion` al principio del archivo `main.py`:

```python
class ConfiguracionSimulacion:
    GRID_FILAS = 15       # Tamaño vertical del cultivo
    GRID_COLUMNAS = 15    # Tamaño horizontal
    NUM_AGENTES = 8       # Cantidad de robots simultáneos
    VELOCIDAD_SIMULACION = 1.0  # Aumentar para ir más rápido
```

## 🧠 Lógica del Sistema (Cómo funciona por dentro)

1.  **Exploración:** El Manager divide el mapa y asigna zonas a cada Agente Físico. Inicializa 5 agentes físicos, cada uno en un thread distinto.
2.  **Sensado:** Los agentes viajan a las celdas y generan datos simulados (humedad, maduración, plagas).
3.  **Comunicación:** El Agente Físico envía datos al Manager mediante *callbacks*.
4.  **Decisión:** El Manager evalúa reglas. Si detecta un jitomate maduro o una plaga crítica, crea una **Instrucción**.
5.  **Interrupción:** El Manager coloca la instrucción en la "Cola de Tareas" del agente más cercano. El agente pausa su exploración, ejecuta la acción (cosechar/curar) y luego retoma su ruta.
