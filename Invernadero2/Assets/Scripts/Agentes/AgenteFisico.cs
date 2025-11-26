using UnityEngine;
using System.Collections;
using System.Collections.Generic; // Necesario para las listas
using System.Linq; // Necesario para ordenar por distancia

public class AgenteFisico : MonoBehaviour
{
    [Header("Configuración Vuelo")]
    public float velocidad = 3.0f;       // Velocidad del dron
    public float alturaVuelo = 1.5f;     // Altura a la que vuela sobre las plantas
    public float distanciaParaParar = 0.5f; // Qué tan cerca se detiene del tomate

    [Header("Configuración Análisis")]
    public float tiempoAnalisis = 2.0f;  // Cuánto tarda en analizar
    public Transform puntoSensor;        // Arrastra el objeto vacío 'SensorPos' aquí

    // Variables internas
    private List<PlantaData> listaDeTomates;
    private int indiceActual = 0;
    private bool estaViajando = true;
    private bool tareaCompletada = false;

    void Start()
    {
        // 1. BUSCAR: Encuentra todos los objetos que tengan el script PlantaData
        var todosLosTomates = FindObjectsOfType<PlantaData>();
        
        // 2. ORDENAR: Los ordena por cercanía para crear una ruta lógica
        listaDeTomates = todosLosTomates.OrderBy(t => Vector3.Distance(transform.position, t.transform.position)).ToList();

        Debug.Log($"[DRON] Ruta calculada: {listaDeTomates.Count} tomates encontrados.");
    }

    void Update()
    {
        // Si terminamos o estamos parados analizando, no hacer nada
        if (tareaCompletada || !estaViajando || listaDeTomates.Count == 0) return;

        // Obtener el objetivo actual de la lista
        PlantaData objetivo = listaDeTomates[indiceActual];

        // Definir el punto de destino (misma posición X/Z del tomate, pero a nuestra altura Y)
        Vector3 destino = new Vector3(objetivo.transform.position.x, alturaVuelo, objetivo.transform.position.z);

        // Moverse hacia el destino
        transform.position = Vector3.MoveTowards(transform.position, destino, velocidad * Time.deltaTime);
        
        // Mirar hacia el destino
        transform.LookAt(destino);

        // Calcular distancia
        float distancia = Vector3.Distance(transform.position, destino);

        // Si estamos cerca, iniciar análisis
        if (distancia < distanciaParaParar)
        {
            StartCoroutine(AnalizarRutina(objetivo));
        }
    }

    IEnumerator AnalizarRutina(PlantaData planta)
    {
        estaViajando = false; // Frenar

        // Dibujar láser rojo (solo se ve en la ventana Scene)
        if (puntoSensor != null)
            Debug.DrawLine(puntoSensor.position, planta.transform.position, Color.red, tiempoAnalisis);

        // Comunicar a la UI (Manager)
        if (AgenteManager.Instance != null)
        {
            AgenteManager.Instance.MostrarAnalisisUI(planta);
        }

        // Esperar tiempo de análisis
        yield return new WaitForSeconds(tiempoAnalisis);

        // Verificar Plaga
        if (planta.tienePlaga)
        {
            planta.MarcarComoEnferma();
            if (AgenteManager.Instance != null)
                AgenteManager.Instance.RegistrarAlerta(planta.name);
        }
        else
        {
            planta.MarcarComoSana();
        }

        planta.yaAnalizada = true;

        // Pasar al siguiente
        indiceActual++;

        if (indiceActual < listaDeTomates.Count)
        {
            estaViajando = true; // Arrancar motores hacia el siguiente
        }
        else
        {
            Debug.Log("[DRON] ✅ Misión Completada. Todos los tomates revisados.");
            tareaCompletada = true;
        }
    }
}