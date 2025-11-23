using UnityEngine;
using TMPro; // Necesario para textos
using UnityEngine.UI;
using System.Collections.Generic;

public class DashboardManager : MonoBehaviour
{
    [Header("Referencias UI")]
    public TextMeshProUGUI textoTiempo;
    public TextMeshProUGUI textoMovimientos;
    public TextMeshProUGUI textoPorcentaje;

    [Header("Referencias Invernadero")]
    // Arrastra aquí tus cubos (plantas) desde la jerarquía
    public List<Renderer> listaDePlantas;

    [Header("Alertas")]
    public GameObject prefabAlertaFlotante; // Lo haremos en el Paso 4
    public Canvas alertaCanvas; // Opcional: asigna un Canvas (Screen Space) para posicionar alertas en pantalla
    public int maxActiveAlerts = 6; // Limita la cantidad de alertas simultáneas
    public float alertaSpacing = 30f; // Espacio (en píxeles para Canvas) o en unidades Y para world-space
    public float riesgoCritico = 0.7f; // Umbral configurable para considerar una planta en peligro

    // Cola para controlar alertas activas y reaprovechar/limitar
    private Queue<GameObject> alertQueue = new Queue<GameObject>();
    // Mapear alertas activas por planta para mostrar la alerta sobre la planta específica
    private Dictionary<int, GameObject> activeAlertsByPlant = new Dictionary<int, GameObject>();
    // Para detener/reiniciar el temporizador de una alerta concreta
    private Dictionary<int, Coroutine> alertCoroutinesByPlant = new Dictionary<int, Coroutine>();

    // Variables simuladas (luego vendrán del Manager real)
    private float tiempoSimulado;
    private int movimientos;
    private bool simulacionActiva = true;

    void Update()
    {   
        if (simulacionActiva)
        {
            tiempoSimulado += Time.deltaTime;
            int porcentajeSuave = (int)(tiempoSimulado * 5) % 100;
            if (porcentajeSuave >= 100) 
            {
                simulacionActiva = false; // ¡STOP!
                Debug.Log("¡Misión Cumplida! Tiempo Final: " + tiempoSimulado);
            }
            ActualizarMetricas(tiempoSimulado, movimientos, porcentajeSuave);
        }
        
        // 4. PRUEBA DE TECLA ESPACIO
        if (Input.GetKeyDown(KeyCode.Space))
        {
            // A. ¡IMPORTANTE! Aquí sumamos 1 al contador
            movimientos++; 

            for(int i = 0; i < listaDePlantas.Count; i++)
            {
                // Simulamos riesgo aleatorio para cada planta
                float riesgoAleatorio = Random.Range(0.0f, 1.0f);
                ActualizarRiesgoPlanta(i, riesgoAleatorio);

                // Gestionamos alertas según el riesgo actual: si es crítico, reportamos/mostramos alerta;
                // si no lo es, eliminamos cualquier alerta previa para esa planta.
                if (riesgoAleatorio > riesgoCritico)
                {
                    // Convertir el índice de la lista a (fila, columna)
                    int totalColumnas = 5; // Debe coincidir con ReportarEstadoCultivo
                    int fila = i / totalColumnas;
                    int columna = i % totalColumnas;
                    // Llamamos al reporte con duracion=0 para que la alerta persista hasta la siguiente evaluación
                    ReportarEstadoCultivo(fila, columna, riesgoAleatorio);
                }
                else
                {
                    // Si la planta ya tenía una alerta activa, la limpiamos inmediatamente
                    ClearAlertForPlant(i);
                }
            }
            // B. Simulamos que la planta en Fila 1, Columna 2 tiene plaga
        }
    }

    // 1. ACTUALIZAR MÉTRICAS (Tu Requisito 3)
    public void ActualizarMetricas(float tiempo, int movs, float porcentaje)
    {
        textoTiempo.text = "Tiempo: " + tiempo.ToString("F2") + "s";
        textoMovimientos.text = "Movimientos: " + movs;
        textoPorcentaje.text = "Analizado: " + porcentaje + "%";
    }

    // 2. MAPA DE RIESGO (Tu Requisito 1)
    // Recibe el índice de la planta y un nivel de riesgo (0.0 es sano, 1.0 es plaga crítica)
    public void ActualizarRiesgoPlanta(int indicePlanta, float nivelRiesgo)
    {
        if (indicePlanta < listaDePlantas.Count)
        {
            // Lerp mezcla colores: 0 es Verde, 1 es Rojo
            Color colorSalud = Color.Lerp(Color.green, Color.red, nivelRiesgo);
            listaDePlantas[indicePlanta].material.color = colorSalud;
        }
    }

    // 3. ALERTAS (Tu Requisito 2)
    public void SimularAlertaAleatoria()
    {
        // Elige una planta al azar para simular que ahí hay plaga
        int indexRandom = Random.Range(0, listaDePlantas.Count);
        Vector3 posicion = listaDePlantas[indexRandom].transform.position;

        // Cambia el color a rojo
        ActualizarRiesgoPlanta(indexRandom, 1.0f);

        // Crea el texto flotante sobre esa planta (usa el índice para evitar duplicados)
        CrearAlertaVisual(indexRandom, posicion, "¡PLAGA DETECTADA!");
    }

    void CrearAlertaVisual(int plantIndex, Vector3 pos, string mensaje, float duracion = 2.0f)
    {
        if (prefabAlertaFlotante == null) return;

        // Si ya hay una alerta activa para esta planta, actualizamos su texto y reiniciamos su temporizador
        if (activeAlertsByPlant.ContainsKey(plantIndex))
        {
            GameObject existing = activeAlertsByPlant[plantIndex];
            if (existing != null)
            {
                var tmpUIexisting = existing.GetComponentInChildren<TextMeshProUGUI>();
                var tmp3Dexisting = existing.GetComponentInChildren<TextMeshPro>();
                if (tmpUIexisting != null) tmpUIexisting.text = mensaje;
                else if (tmp3Dexisting != null) tmp3Dexisting.text = mensaje;

                // Reposicionar encima de la planta
                if (alertaCanvas != null && Camera.main != null)
                {
                    Vector3 screenPos = Camera.main.WorldToScreenPoint(pos + Vector3.up * 2);
                    RectTransform rt = existing.GetComponent<RectTransform>();
                    if (rt != null) rt.position = screenPos;
                    else existing.transform.position = screenPos;
                }
                else
                {
                    existing.transform.position = pos + Vector3.up * 2;
                    if (Camera.main != null) existing.transform.LookAt(Camera.main.transform);
                }

                // Reiniciamos solo la coroutine de esta alerta (no todas)
                if (alertCoroutinesByPlant.TryGetValue(plantIndex, out Coroutine existingCoroutine) && existingCoroutine != null)
                {
                    StopCoroutine(existingCoroutine);
                    alertCoroutinesByPlant.Remove(plantIndex);
                }
                Coroutine newC = StartCoroutine(RemoveAlertAfter(plantIndex, existing, duracion));
                alertCoroutinesByPlant[plantIndex] = newC;
                return;
            }
        }

        // Crear nueva alerta encima de la planta (sin apilar globalmente)
        if (alertaCanvas != null && Camera.main != null)
        {
            GameObject alerta = Instantiate(prefabAlertaFlotante, alertaCanvas.transform);
            var tmpUI = alerta.GetComponentInChildren<TextMeshProUGUI>();
            var tmp3D = alerta.GetComponentInChildren<TextMeshPro>();
            if (tmpUI != null) tmpUI.text = mensaje;
            else if (tmp3D != null) tmp3D.text = mensaje;

            Vector3 screenPos = Camera.main.WorldToScreenPoint(pos + Vector3.up * 2);
            RectTransform rt = alerta.GetComponent<RectTransform>();
            if (rt != null) rt.position = screenPos;
            else alerta.transform.position = screenPos;

            activeAlertsByPlant[plantIndex] = alerta;
            Coroutine c = StartCoroutine(RemoveAlertAfter(plantIndex, alerta, duracion));
            alertCoroutinesByPlant[plantIndex] = c;
            return;
        }

        // Fallback: world-space popup justo encima de la planta
        GameObject alertaWorld = Instantiate(prefabAlertaFlotante, pos + Vector3.up * 2, Quaternion.identity);
        var tmpWorld = alertaWorld.GetComponentInChildren<TextMeshPro>();
        if (tmpWorld != null) tmpWorld.text = mensaje;
        if (Camera.main != null) alertaWorld.transform.LookAt(Camera.main.transform);
        activeAlertsByPlant[plantIndex] = alertaWorld;
        Coroutine cWorld = StartCoroutine(RemoveAlertAfter(plantIndex, alertaWorld, duracion));
        alertCoroutinesByPlant[plantIndex] = cWorld;
    }

    System.Collections.IEnumerator RemoveAlertAfter(int plantIndex, GameObject alerta, float duracion)
    {
        yield return new WaitForSeconds(duracion);
        if (alerta != null) Destroy(alerta);
        if (activeAlertsByPlant.ContainsKey(plantIndex) && activeAlertsByPlant[plantIndex] == alerta)
        {
            activeAlertsByPlant.Remove(plantIndex);
        }
        if (alertCoroutinesByPlant.ContainsKey(plantIndex) && alertCoroutinesByPlant[plantIndex] != null)
        {
            // Only remove the entry if it references this coroutine (it usually will)
            alertCoroutinesByPlant.Remove(plantIndex);
        }
    }

    // Elimina inmediatamente la alerta asociada a una planta (si existe)
    void ClearAlertForPlant(int plantIndex)
    {
        if (alertCoroutinesByPlant.TryGetValue(plantIndex, out Coroutine c) && c != null)
        {
            StopCoroutine(c);
            alertCoroutinesByPlant.Remove(plantIndex);
        }

        if (activeAlertsByPlant.TryGetValue(plantIndex, out GameObject go) && go != null)
        {
            Destroy(go);
            activeAlertsByPlant.Remove(plantIndex);
        }
    }
    // ESTA ES LA FUNCIÓN QUE TUS COMPAÑEROS USARÁN
    // filas: número total de filas en tu invernadero (ej. 4)
    // columnas: número total de columnas (ej. 5)
    public void ReportarEstadoCultivo(int fila, int columna, float nivelRiesgo)
    {
        // Convertimos coordenada (x, y) a índice de lista (0, 1, 2...)
        // Fórmula: (FilaActual * TotalColumnas) + ColumnaActual
        int totalColumnas = 5; // <--- AJUSTA ESTO A TU ESCENA REAL

        int indiceLista = (fila * totalColumnas) + columna;

        // Verificamos que no nos salgamos de la lista
        if (indiceLista >= 0 && indiceLista < listaDePlantas.Count)
        {
            // 1. Cambiamos el color
            ActualizarRiesgoPlanta(indiceLista, nivelRiesgo);

            // 2. Si es crítico (Riesgo alto), mostramos la alerta
            if (nivelRiesgo > 0.7f) // Si el riesgo es mayor al 70%
            {
                Vector3 pos = listaDePlantas[indiceLista].transform.position;
                CrearAlertaVisual(indiceLista, pos, "¡ALERTA " + fila + "-" + columna + "!");
            }
        }
        else
        {
            Debug.LogError("¡Coordenada fuera de rango! Revisa tus filas/columnas");
        }
    }
}