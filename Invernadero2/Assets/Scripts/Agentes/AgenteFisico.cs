using UnityEngine;
using System.Collections;
using System.Collections.Generic; 
using System.Linq; 

public class AgenteFisico : MonoBehaviour
{
    [Header("Configuración Vuelo")]
    public float velocidad = 3.0f;       // Velocidad del dron
    public float alturaVuelo = 1.5f;     // Altura a la que vuela sobre las plantas
    public float distanciaParaParar = 0.5f; // Qué tan cerca se detiene del tomate

    [Header("Configuración Análisis")]
    public float tiempoAnalisis = 2.0f;  // Cuánto tarda en analizar
    public Transform puntoSensor;       

    // Variables internas
    private List<PlantaData> listaDeTomates;
    private int indiceActual = 0;
    private bool estaViajando = true;
    private bool tareaCompletada = false;

    void Start()
    {
        // Encuentra todos los objetos que tengan el script PlantaData
        var todosLosTomates = FindObjectsOfType<PlantaData>();
        
        // Los ordena por cercanía para crear una ruta lógica
        listaDeTomates = todosLosTomates.OrderBy(t => Vector3.Distance(transform.position, t.transform.position)).ToList();

        Debug.Log($"[DRON] Ruta calculada: {listaDeTomates.Count} tomates encontrados.");
    }

    void Update()
    {
        // Si terminamos o estamos parados analizando, no hacer nada
        if (tareaCompletada || !estaViajando || listaDeTomates.Count == 0) return;

        // Obtener el objetivo actual de la lista
        PlantaData objetivo = listaDeTomates[indiceActual];

        // Definir el punto de destino (misma posición X/Z del tomate, pero a la altura Y)
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
        estaViajando = false; 

        // Detección inmediata al llegar
        if (planta.tienePlaga)
        {
            planta.MarcarComoEnferma();
            if (AgenteManager.Instance != null)
                AgenteManager.Instance.RegistrarAlerta(planta.nombreComun); // ¡Alerta YA!
        }
        else
        {
            planta.MarcarComoSana();
        }

        // Comunicar estado normal
        if (AgenteManager.Instance != null)
            AgenteManager.Instance.MostrarAnalisisUI(planta);

        // Dibujar láser
        if (puntoSensor != null)
            Debug.DrawLine(puntoSensor.position, planta.transform.position, Color.red, tiempoAnalisis);

        // Esperar simulando recolección de datos detallados
        yield return new WaitForSeconds(tiempoAnalisis);

        planta.yaAnalizada = true;
        indiceActual++;

        if (indiceActual < listaDeTomates.Count)
        {
            estaViajando = true;
        }
        else
        {
            Debug.Log("[DRON] Misión Completada.");
            tareaCompletada = true;
        }
    }
}