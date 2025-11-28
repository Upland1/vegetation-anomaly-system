using UnityEngine;

public class PlantaData : MonoBehaviour
{
    [Header("Datos Identificación")]
    public string nombreComun = ""; 
    
    [Header("Datos Biológicos")]
    public bool tienePlaga = false; 
    [Range(0, 100)] public float humedad = 65.0f;
    [Range(0, 10)] public float nivelMaduracion = 5.0f;
    [Range(0, 100)] public float saludGeneral = 80.0f; // ✅ AGREGADO
    
    [HideInInspector] public bool yaAnalizada = false;
    
    [Header("Configuración Visual")]
    public Color colorSano = new Color32(255, 4, 0, 255);
    public Color colorEnfermo = new Color32(133, 111, 20, 255);
    
    private Renderer miRenderer;
    
    void Start()
    {
        // Generar nombre automático si está vacío
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
        saludGeneral = Mathf.Max(20f, saludGeneral - 30f); // Reduce salud
        ActualizarColor();
    }
    
    public void MarcarComoSana()
    {
        tienePlaga = false;
        saludGeneral = Mathf.Min(100f, saludGeneral + 20f); // Mejora salud
        ActualizarColor();
    }
    
    void ActualizarColor()
    {
        if (miRenderer != null)
        {
            miRenderer.material.color = tienePlaga ? colorEnfermo : colorSano;
        }
    }
    
    // ══════════════════════════════════════════════════════════════
    // MÉTODOS REQUERIDOS POR AgenteManager
    // ══════════════════════════════════════════════════════════════
    
    /// <summary>
    /// Verifica si la planta está lista para cosechar
    /// </summary>
    public bool EstaListaParaCosechar()
    {
        return nivelMaduracion >= 8.0f && saludGeneral >= 60f;
    }
    
    /// <summary>
    /// Verifica si la planta está muy inmadura/verde
    /// </summary>
    public bool EstaMuyVerde()
    {
        return nivelMaduracion <= 3.0f;
    }
    
    /// <summary>
    /// Verifica si tiene plaga activa
    /// </summary>
    public bool TienePlagaActiva()
    {
        return tienePlaga;
    }
    
    /// <summary>
    /// Verifica si tiene alertas críticas (IoT simulado)
    /// Puedes ajustar los umbrales según tu lógica
    /// </summary>
    public bool TieneAlertasCriticas()
    {
        return humedad < 30f || humedad > 90f || saludGeneral < 40f;
    }
}