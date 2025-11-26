using UnityEngine;

using UnityEngine;

public class PlantaData : MonoBehaviour
{
    [Header("Datos Biológicos")]
    public bool tienePlaga = false; // ¡Marca esto para probar!
    [Range(0, 100)] public float humedad = 65.0f;
    [Range(0, 10)] public float nivelMaduracion = 5.0f; 
    
    [HideInInspector] public bool yaAnalizada = false;

    [Header("Configuración Visual")]
    public Color colorSano = new Color32(255, 4, 0, 255);
    public Color colorEnfermo = new Color32(133, 111, 20, 255);

    // Variable privada interna (ya no necesitas arrastrar nada)
    private Renderer miRenderer;

    void Start()
    {
        // 1. BUSCAR AUTOMÁTICAMENTE: El script busca el Renderer en ESTE mismo objeto
        miRenderer = GetComponent<Renderer>();

        if (miRenderer == null)
        {
            Debug.LogError($"[ERROR] El objeto '{name}' tiene el script PlantaData pero NO tiene un Mesh Renderer para pintar.");
        }
        else
        {
            ActualizarColor();
        }
    }

    public void MarcarComoEnferma()
    {
        tienePlaga = true;
        ActualizarColor();
    }

    public void MarcarComoSana()
    {
        tienePlaga = false;
        ActualizarColor();
    }

    void ActualizarColor()
    {
        if (miRenderer != null)
        {
            // Pinta directamente este objeto
            miRenderer.material.color = tienePlaga ? colorEnfermo : colorSano;
        }
    }
}