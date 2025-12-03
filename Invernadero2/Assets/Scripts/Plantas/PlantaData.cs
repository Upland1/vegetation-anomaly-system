using UnityEngine;

public class PlantaData : MonoBehaviour
{
    [Header("Datos Identificación")]
    public string nombreComun = "";
    
    [Header("Datos Biológicos")]
    public bool tienePlaga = false;
    [Range(0, 100)] public float humedad = 65.0f;
    [Range(0, 10)] public float nivelMaduracion = 5.0f;
    [Range(0, 100)] public float saludGeneral = 80.0f;
    
    [Header("Estado Dinámico del Cultivo")]
    public bool cosechada = false;
    [Range(0, 10)] public float nivelPlaga = 0f;
    public float tiempoDesdeUltimoPesticida = 0f;
    public float velocidadCrecimiento = 0.01f;
    
    [Header("Sistema de Riego")]
    public float velocidadDeshidratacion = 0.5f; // Humedad que pierde por segundo
    public float tiempoDesdeUltimoRiego = 0f;
    public int vecesRegada = 0;
    
    [HideInInspector] public bool yaAnalizada = false;
    
    [Header("Configuración Visual")]
    public Color colorSano = new Color32(255, 4, 0, 255);
    public Color colorEnfermo = new Color32(133, 111, 20, 255);
    public Color colorCosechado = new Color32(100, 100, 100, 255);
    public Color colorSeco = new Color32(139, 69, 19, 255); // Color café para sequía
    
    private Renderer miRenderer;
    
    void Start()
    {
        if (string.IsNullOrEmpty(nombreComun))
        {
            nombreComun = $"Tomate {Random.Range(100, 999)}";
        }
        
        miRenderer = GetComponent<Renderer>();
        
        if (tienePlaga)
        {
            nivelPlaga = Random.Range(3f, 7f);
        }
        
        if (miRenderer != null) 
            ActualizarColor();
    }
    
    void Update()
    {
        if (cosechada) return;
        
        // ═══════════════════════════════════════════════════════
        // SISTEMA DE DESHIDRATACIÓN NATURAL
        // ═══════════════════════════════════════════════════════
        tiempoDesdeUltimoRiego += Time.deltaTime;
        
        // La planta pierde humedad con el tiempo
        if (humedad > 0)
        {
            humedad -= velocidadDeshidratacion * Time.deltaTime;
            humedad = Mathf.Clamp(humedad, 0f, 100f);
        }
        
        // Si la humedad es muy baja, afecta la salud y el crecimiento
        if (humedad < 30f)
        {
            saludGeneral -= Time.deltaTime * 0.2f; // Pierde salud por sequía
            velocidadCrecimiento = 0.005f; // Crece más lento
            
            ActualizarColor(); // Mostrar visualmente el estrés hídrico
        }
        else
        {
            velocidadCrecimiento = 0.01f; // Velocidad normal
        }
        
        // ═══════════════════════════════════════════════════════
        // CRECIMIENTO NATURAL
        // ═══════════════════════════════════════════════════════
        if (nivelMaduracion < 10f && humedad > 20f) // Solo crece si tiene agua
        {
            nivelMaduracion += Time.deltaTime * velocidadCrecimiento;
            nivelMaduracion = Mathf.Clamp(nivelMaduracion, 0f, 10f);
        }
        
        // ═══════════════════════════════════════════════════════
        // PROPAGACIÓN DE PLAGA
        // ═══════════════════════════════════════════════════════
        if (tienePlaga)
        {
            tiempoDesdeUltimoPesticida += Time.deltaTime;
            
            if (tiempoDesdeUltimoPesticida > 20f)
            {
                nivelPlaga += Time.deltaTime * 0.05f;
                nivelPlaga = Mathf.Clamp(nivelPlaga, 0f, 10f);
                
                saludGeneral -= Time.deltaTime * 0.3f;
                saludGeneral = Mathf.Clamp(saludGeneral, 0f, 100f);
                
                ActualizarColor();
            }
        }
        else
        {
            // Recuperación gradual solo si tiene suficiente agua
            if (saludGeneral < 100f && humedad > 50f)
            {
                saludGeneral += Time.deltaTime * 0.1f;
                saludGeneral = Mathf.Clamp(saludGeneral, 0f, 100f);
            }
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // ACCIÓN: REGAR LA PLANTA
    // ═══════════════════════════════════════════════════════════
    /// <summary>
    /// Riega la planta, aumentando su humedad
    /// </summary>
    /// <param name="cantidadAgua">Cantidad de agua a aplicar (0-100)</param>
    public void Regar(float cantidadAgua = 40f)
    {
        float humedadAnterior = humedad;
        
        humedad += cantidadAgua;
        humedad = Mathf.Clamp(humedad, 0f, 100f);
        
        tiempoDesdeUltimoRiego = 0f;
        vecesRegada++;
        
        // Mejora ligera de salud si estaba seca
        if (humedadAnterior < 30f)
        {
            saludGeneral += 10f;
            saludGeneral = Mathf.Clamp(saludGeneral, 0f, 100f);
        }
        
        Debug.Log($"[PLANTA] {nombreComun} REGADA: {humedadAnterior:F1}% → {humedad:F1}% " +
                  $"(Total riegos: {vecesRegada})");
        
        ActualizarColor();
    }
    
    // ═══════════════════════════════════════════════════════════
    // OTRAS ACCIONES
    // ═══════════════════════════════════════════════════════════
    
    public void AplicarPesticida()
    {
        nivelPlaga = Mathf.Max(0, nivelPlaga - 5f);
        tiempoDesdeUltimoPesticida = 0f;
        
        if (nivelPlaga <= 0.5f)
        {
            nivelPlaga = 0f;
            tienePlaga = false;
            MarcarComoSana();
            Debug.Log($"[PLANTA] {nombreComun} - Plaga ELIMINADA");
        }
        else
        {
            Debug.Log($"[PLANTA] {nombreComun} - Plaga reducida a {nivelPlaga:F1}/10");
        }
        
        ActualizarColor();
    }
    
    public void Cosechar()
    {
        cosechada = true;
        
        if (miRenderer != null)
        {
            miRenderer.material.color = colorCosechado;
        }
        
        Debug.Log($"[PLANTA] {nombreComun} COSECHADA - Madurez: {nivelMaduracion:F1}/10");
        
        Invoke(nameof(DesactivarPlanta), 0.5f);
    }
    
    void DesactivarPlanta()
    {
        gameObject.SetActive(false);
    }
    
    public void MarcarComoEnferma()
    {
        tienePlaga = true;
        if (nivelPlaga == 0)
            nivelPlaga = Random.Range(3f, 7f);
        
        saludGeneral = Mathf.Max(20f, saludGeneral - 30f);
        ActualizarColor();
    }
    
    public void MarcarComoSana()
    {
        tienePlaga = false;
        nivelPlaga = 0f;
        saludGeneral = Mathf.Min(100f, saludGeneral + 20f);
        ActualizarColor();
    }
    
    void ActualizarColor()
    {
        if (miRenderer != null && !cosechada)
        {
            // Prioridad: Plaga > Sequía > Sano
            if (tienePlaga)
            {
                float factor = 1f - (nivelPlaga / 10f) * 0.5f;
                miRenderer.material.color = colorEnfermo * factor;
            }
            else if (humedad < 30f) // Estrés hídrico
            {
                miRenderer.material.color = Color.Lerp(colorSeco, colorSano, humedad / 30f);
            }
            else
            {
                miRenderer.material.color = colorSano;
            }
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // MÉTODOS DE CONSULTA
    // ═══════════════════════════════════════════════════════════
    
    public bool EstaListaParaCosechar()
    {
        return nivelMaduracion >= 8.0f && saludGeneral >= 60f && !cosechada;
    }
    
    public bool EstaMuyVerde()
    {
        return nivelMaduracion <= 3.0f;
    }
    
    public bool TienePlagaActiva()
    {
        return tienePlaga && nivelPlaga > 0;
    }
    
    public bool TieneAlertasCriticas()
    {
        return humedad < 30f || humedad > 90f || saludGeneral < 40f;
    }
    
    /// <summary>
    /// Nueva: Verifica si necesita riego urgente
    /// </summary>
    public bool NecesitaRiego()
    {
        return humedad < 30f && !cosechada;
    }
    
    /// <summary>
    /// Nueva: Verifica si necesita riego preventivo
    /// </summary>
    public bool NecesitaRiegoPreventivo()
    {
        return humedad < 50f && !cosechada;
    }
    
    public string ObtenerEstadoCompleto()
    {
        return $"{nombreComun}: Madurez={nivelMaduracion:F1}, Humedad={humedad:F0}%, " +
               $"Salud={saludGeneral:F0}%, Plaga={nivelPlaga:F1}, Riegos={vecesRegada}";
    }
}