# Guía de Instalación y Ejecución - Simulador de Invernadero

## Contenido

- [¿Qué es esto?](#qué-es-esto)
- [Antes de empezar](#antes-de-empezar)
- [Instalación](#instalación)
- [Primeros pasos](#primeros-pasos)
- [Cómo ejecutar](#cómo-ejecutar)
- [La interfaz](#la-interfaz)
- [Ayuda y errores comunes](#ayuda-y-errores-comunes)

---

## ¿Qué es esto?

Es una simulación hecha en Unity que implementa un sistema de agentes (robots virtuales) para monitorear y gestionar un cultivo de tomates. Cada agente puede moverse por el invernadero, detectar plantas, identificar plagas y ejecutar acciones como cosechas. Todo esto se controla desde un dashboard que muestra métricas en tiempo real.

**Lo más importante:** Funciona con agentes distribuidos que toman decisiones de forma independiente, coordinados por un manager central.

---

## Antes de empezar

### Qué necesitas

**Hardware:**
- Una PC con Windows 10 o 11 (también funciona en Linux/Mac pero sin soporte)
- Mínimo 8 GB de RAM, 16 GB es lo ideal
- Al menos 15 GB libres en el disco duro
- Una tarjeta gráfica decente (GTX 1050 en adelante es suficiente)

**Software:**
- Unity 6000.2.13f1 (esa versión específica)
- Git instalado
- Visual Studio Community 2022 (opcional pero útil para debugging)

---

## Instalación

### 1. Instala Unity Hub y la versión correcta

1. Ve a https://unity.com/download y descarga **Unity Hub**
2. Una vez instalado, abre Unity Hub
3. En la sección "Installs" (Instalaciones), haz clic en "Install Editor"
4. Busca y descarga la versión **6000.2.13f1**
5. Selecciona:
   - Visual Studio Community 2022 (para los scripts)
   - La documentación (opcional pero útil)
6. Espera a que termine (toma un rato, depende de tu conexión)

### 2. Descarga el proyecto

Abre PowerShell (o CMD) en la carpeta donde quieras guardar el proyecto:

```powershell
git clone https://github.com/Upland1/vegetation-anomaly-system.git
cd vegetation-anomaly-system/Invernadero2
```

### 3. Abre el proyecto

1. Abre Unity Hub
2. Ve a "Projects"
3. Presiona "Open"
4. Navega hasta `vegetation-anomaly-system/Invernadero2` y selecciona esa carpeta
5. Unity cargará el proyecto (la primera vez tarda unos 10 minutos)

> **Nota:** En el proceso, Unity va a sincronizar todo, compilar los scripts, cargar los assets... no cierre nada hasta que termine.

---

## Primeros pasos

Una vez que el proyecto esté abierto en Unity, hay algunas cosas que vale la pena revisar:

### Escenas disponibles

En la carpeta `Assets/Scenes` encontrarás:

- **DronRobot.unity** - Escena simple con un dron. Útil para ver cómo se mueven las cosas
- **tomates.unity** - La escena principal. Aquí está el invernadero completo
- **PlagueSimulation.unity** - Una versión enfocada en detectar y combatir plagas

### Configurar los agentes

Si quieres cambiar cuántos robots hay, qué tan rápido se mueven, cuán lejos ven, etc.:

1. En la escena, busca el objeto "AgenteManager" en el panel de la derecha (Hierarchy)
2. Haz clic en él y mira el panel "Inspector" (abajo a la derecha)
3. Ahí verás los valores que puedes cambiar

### Configurar las plantas

Las plantas tienen datos que puedes ajustar:

1. Selecciona una planta en la escena
2. En el Inspector, verás "PlantaData"
3. Puedes cambiar: maduración, riesgo de plagas, estado de salud, etc.

### Dashboard

El dashboard es lo que muestra las métricas:

1. Busca "DashboardManager" en la Hierarchy
2. En el Inspector, revisa qué está conectado a qué
3. Todos los campos de referencia deben estar asignados (no deben estar vacíos)

---

## Cómo ejecutar

### En el editor (para desarrollar)

1. En el panel de arriba, busca el botón **Play** (▶️)
2. O simplemente presiona **Ctrl + P**
3. Verás cómo funciona todo en la ventana del centro (Game view)

**Mientras está corriendo:**
- **ESC** - Detiene la simulación
- **P** - Pausa/reanuda
- **F** - Cambia la vista de cámara
- **Ratón** - Interactúa con el dashboard

### Crear un ejecutable (para compartir/ejecutar sin editor)

1. Ve a **File** > **Build Settings**
2. Verifica que las escenas que quieras usar estén en "Scenes In Build"
3. Selecciona la plataforma **PC, Mac & Linux Standalone**
4. Presiona **Build**
5. Elige una carpeta para guardar el resultado
6. Espera (esto puede tomar 10-30 minutos)

Una vez que termine, abre el `.exe` que se generó y la simulación se ejecutará como una aplicación normal.

---

## La interfaz

### Qué ves en pantalla

El dashboard muestra básicamente:

- **Agentes activos** - Cuántos robots están haciendo algo
- **Plantas** - El estado total de las plantas
- **Plagas** - Si se han detectado problemas
- **Cosechas** - Cuántas plantas se han cosechado

### Código de colores

Las plantas se representan con colores según su estado:

| Color | Qué significa |
|-------|---|
| Verde | Bien, sin problemas |
| Amarillo | Algo raro, hay que vigilar |
| Rojo | Mal, hay plagas o problemas serios |
| Morado | Lista para cosechar |
| Gris | No se ha explorado todavía |

### Botones principales

- **Play** - Inicia
- **Pause** - Pausa
- **Reset** - Vuelve al principio
- **Settings** - Configura parámetros
- **Stats** - Ve el reporte

---

## Cómo funciona por adentro

En pocas palabras:

1. **Los robots empiezan** - Aparecen en la escena
2. **Exploran** - Se mueven por el invernadero
3. **Detectan plantas** - Recopilan información (humedad, maduración, plagas)
4. **Reportan al manager** - Le envían los datos
5. **El manager decide** - Analiza si hay que cosechar o tratar algo
6. **Se ejecutan acciones** - Los robots cosechan o aplican tratamientos
7. **Se actualiza el dashboard** - Ves los cambios en tiempo real

---

## Ayuda y errores comunes

### "No puedo abrir el proyecto en Unity"

**Probable causa:** No tienes la versión 6000.2.13f1 instalada.

**Solución:**
1. Abre Unity Hub
2. En "Installs", comprueba que tienes la versión 6000.2.13f1
3. Si no la tienes, instálala desde "Install Editor"

### Los robots no se mueven

**Probable causa:** La simulación está en pausa o hay un error de script.

**Solución:**
1. Presiona `P` para asegurate de que no está pausada
2. Abre la **Consola** desde **Window > General > Console**
3. Si hay mensajes rojos, significa que hay errores. Revisa qué dice
4. Comprueba que el script `AgenteFisico.cs` está en `Assets/Scripts/Agentes/`

### El dashboard no muestra nada

**Probable causa:** Falta de referencias en el inspector o el manager no está en la escena.

**Solución:**
1. Selecciona "DashboardManager" en la Hierarchy
2. En el Inspector, asegúrate que TODOS los campos tengan algo asignado
3. Si faltan referencias, asígnalas manualmente desde el proyecto

### La aplicación se congela

**Probable causa:** Demasiados agentes o scripts con problemas.

**Solución:**
1. Reduce el número de agentes en AgenteManager
2. Cierra otras aplicaciones para liberar RAM
3. En la Consola, busca si hay bucles infinitos o deadlocks
4. Reinicia Unity si nada funciona

### Errores "CS..." en la consola

Son errores de compilación en los scripts C#.

**Solución:**
1. Lee el mensaje de error - te dice exactamente qué archivo tiene el problema
2. Abre ese archivo desde `Assets/Scripts/`
3. Busca la línea mencionada en el error
4. Corrígela (puede ser una falta de ortografía, una referencia rota, etc.)
5. Guarda con **Ctrl + S** - Unity recompilará automáticamente

---

## Resumen rápido

Si tienes prisa y solo quieres que funcione:

1. Descarga e instala Unity Hub
2. Instala Unity 6000.2.13f1
3. Clona el repo: `git clone https://github.com/Upland1/vegetation-anomaly-system.git`
4. Abre la carpeta `Invernadero2` en Unity Hub
5. Espera a que cargue todo (unos 10 minutos)
6. Presiona **Play** ▶️
7. Listo, ya funciona

---

## Más info

- Los scripts están en `Assets/Scripts/`
- Las escenas en `Assets/Scenes/`
- Los modelos 3D en `Assets/Models/tomatoe/`
- Los materiales en `Assets/Materials/`

---

**Última actualización:** Diciembre 2025  
**Versión de Unity usada:** 6000.2.13f1
