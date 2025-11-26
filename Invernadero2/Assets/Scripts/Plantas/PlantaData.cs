using UnityEngine;

public class PlantaData : MonoBehaviour
{
    [Header("Datos Identificación")]
    // ¡Esta es la variable que faltaba!
    public string nombreComun = ""; 

    [Header("Datos Biológicos")]
    public bool tienePlaga = false; 
    [Range(0, 100)] public float humedad = 65.0f;
    [Range(0, 10)] public float nivelMaduracion = 5.0f; 
    
    [HideInInspector] public bool yaAnalizada = false;

    [Header("Configuración Visual")]
    // Tus colores personalizados (Rojo vivo y Marrón enfermo)
    public Color colorSano = new Color32(255, 4, 0, 255);
    public Color colorEnfermo = new Color32(133, 111, 20, 255);

    private Renderer miRenderer;

    void Start()
    {
        // Generar nombre automático si está vacío (Ej: "Tomate 402")
        if (string.IsNullOrEmpty(nombreComun))
        {
            nombreComun = $"Tomate {Random.Range(100, 999)}";
        }

        // Buscar el pintor automáticamente
        miRenderer = GetComponent<Renderer>();
        
        // Aplicar color inicial
        if (miRenderer != null) ActualizarColor();
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
            miRenderer.material.color = tienePlaga ? colorEnfermo : colorSano;
        }
    }
}