using UnityEngine;
using TMPro;
using System.Collections.Generic;
using System.Linq;

public class UIController : MonoBehaviour
{
    [Header("Referencias UI")]
    public TextMeshProUGUI textoEstadoGeneral;
    public TextMeshProUGUI textoAlertas;
    public TextMeshProUGUI textoHistorial;
    public TextMeshProUGUI textoPoliticasAgente;
    
    [Header("Configuración UI")]
    public int maxLineasHistorial = 15;
    
    [Header("═══ POLÍTICAS DEL AGENTE DE RIEGO ═══")]
    [Tooltip("Umbral de humedad para riego urgente")]
    [Range(0, 50)]
    public float umbralRiegoUrgente = 30f;
    
    [Tooltip("Umbral de humedad para riego preventivo")]
    [Range(30, 70)]
    public float umbralRiegoPreventivo = 50f;
    
    [Tooltip("Cantidad de agua por riego")]
    [Range(20, 60)]
    public float cantidadAguaPorRiego = 40f;
    
    [Tooltip("Intervalo de análisis del campo (segundos)")]
    [Range(1, 10)]
    public float intervaloAnalisis = 3f;
    
    [Tooltip("Activar riego automático")]
    public bool riegoAutomaticoActivo = true;
    
    // Estadísticas
    private int totalAlertas = 0;
    private int totalAnalizadas = 0;
    private int totalCosechadas = 0;
    private int totalRiegosRealizados = 0;
    private int totalRiegosUrgentes = 0;
    private int totalRiegosPreventivos = 0;
    
    private Queue<string> historialAcciones = new Queue<string>();
    
    // Sistema de análisis periódico
    private float tiempoDesdeUltimoAnalisis = 0f;
    private List<PlantaData> todasLasPlantas = new List<PlantaData>();
    private bool sistemaInicializado = false;
    
    void Start()
    {
        ActualizarUI();
        
        // Si no se inicializó desde el Manager, buscar plantas manualmente
        if (todasLasPlantas.Count == 0)
        {
            Invoke(nameof(BuscarPlantasManualmente), 1f);
        }
    }
    
    void Update()
    {
        if (!riegoAutomaticoActivo || !sistemaInicializado) return;
        
        tiempoDesdeUltimoAnalisis += Time.deltaTime;
        
        // Ejecutar políticas del agente cada X segundos
        if (tiempoDesdeUltimoAnalisis >= intervaloAnalisis)
        {
            tiempoDesdeUltimoAnalisis = 0f;
            EjecutarPoliticasDeRiego();
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // INICIALIZACIÓN (LLAMADO POR AGENTEMANAGER)
    // ═══════════════════════════════════════════════════════════
    
    /// <summary>
    /// Inicializa el agente de riego con la lista de plantas del Manager
    /// </summary>
    public void InicializarConPlantas(List<PlantaData> plantas)
    {
        todasLasPlantas = plantas;
        sistemaInicializado = true;
        
        Debug.Log($"[AGENTE RIEGO] 🌱 Inicializado con {todasLasPlantas.Count} plantas");
        MostrarPoliticas();
        
        AgregarHistorial($"[SISTEMA] Agente de riego inicializado con {plantas.Count} plantas");
    }
    
    void BuscarPlantasManualmente()
    {
        todasLasPlantas = FindObjectsOfType<PlantaData>().ToList();
        
        if (todasLasPlantas.Count > 0)
        {
            sistemaInicializado = true;
            Debug.Log($"[AGENTE RIEGO] 🌱 {todasLasPlantas.Count} plantas detectadas manualmente");
            MostrarPoliticas();
        }
        else
        {
            Debug.LogWarning("[AGENTE RIEGO] ⚠️ No se detectaron plantas en la escena");
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // POLÍTICAS DEL AGENTE DE RIEGO
    // ═══════════════════════════════════════════════════════════
    
    void MostrarPoliticas()
    {
        string politicas = $"═══ AGENTE DE RIEGO AUTOMÁTICO ═══\n" +
                          $"P1: IF humedad < {umbralRiegoUrgente}% THEN regar_urgente()\n" +
                          $"P2: IF humedad < {umbralRiegoPreventivo}% THEN regar_preventivo()\n" +
                          $"P3: Priorizar plantas con salud < 50%\n" +
                          $"P4: Analizar campo cada {intervaloAnalisis}s\n" +
                          $"Estado: {(riegoAutomaticoActivo ? "ACTIVO ✓" : "INACTIVO ✗")}";
        
        if (textoPoliticasAgente != null)
        {
            textoPoliticasAgente.text = politicas;
            textoPoliticasAgente.color = riegoAutomaticoActivo ? Color.cyan : Color.gray;
        }
        
        Debug.Log($"[AGENTE RIEGO] {politicas}");
    }
    
    /// <summary>
    /// Ejecuta las políticas de riego automático del agente
    /// </summary>
    void EjecutarPoliticasDeRiego()
    {
        if (todasLasPlantas.Count == 0)
        {
            BuscarPlantasManualmente();
            return;
        }
        
        // POLÍTICA 1: Riego Urgente (Prioridad Alta)
        var plantasUrgentes = todasLasPlantas
            .Where(p => p != null && !p.cosechada && p.humedad < umbralRiegoUrgente)
            .OrderBy(p => p.humedad) // Más secas primero
            .ThenBy(p => p.saludGeneral) // Menos sanas primero
            .ToList();
        
        foreach (var planta in plantasUrgentes)
        {
            RegarPlanta(planta, true);
        }
        
        // POLÍTICA 2: Riego Preventivo (Prioridad Media)
        var plantasPreventivas = todasLasPlantas
            .Where(p => p != null && !p.cosechada && 
                   p.humedad >= umbralRiegoUrgente && 
                   p.humedad < umbralRiegoPreventivo)
            .OrderBy(p => p.saludGeneral) // Priorizar las menos sanas
            .Take(3) // Máximo 3 por ciclo para no saturar
            .ToList();
        
        foreach (var planta in plantasPreventivas)
        {
            RegarPlanta(planta, false);
        }
    }
    
    /// <summary>
    /// Acción del agente: Regar una planta específica
    /// </summary>
    void RegarPlanta(PlantaData planta, bool esUrgente)
    {
        if (planta == null || planta.cosechada) return;
        
        float humedadAntes = planta.humedad;
        
        // Ejecutar acción de riego
        planta.Regar(cantidadAguaPorRiego);
        
        totalRiegosRealizados++;
        
        if (esUrgente)
        {
            totalRiegosUrgentes++;
            RegistrarAlerta(planta, -1, $"💧 RIEGO URGENTE aplicado");
            AgregarHistorial($"[URGENTE] 💧 Riego a {planta.nombreComun} " +
                           $"({humedadAntes:F0}% → {planta.humedad:F0}%)");
        }
        else
        {
            totalRiegosPreventivos++;
            AgregarHistorial($"[PREVENTIVO] 💧 Riego a {planta.nombreComun} " +
                           $"({humedadAntes:F0}% → {planta.humedad:F0}%)");
        }
        
        // Actualizar estadísticas en UI
        ActualizarEstadisticasRiego();
    }
    
    void ActualizarEstadisticasRiego()
    {
        if (textoPoliticasAgente != null)
        {
            textoPoliticasAgente.text = $"═══ AGENTE DE RIEGO AUTOMÁTICO ═══\n" +
                $"Total riegos: {totalRiegosRealizados}\n" +
                $"  • Urgentes: {totalRiegosUrgentes}\n" +
                $"  • Preventivos: {totalRiegosPreventivos}\n" +
                $"Próximo análisis: {intervaloAnalisis - tiempoDesdeUltimoAnalisis:F1}s\n" +
                $"Estado: {(riegoAutomaticoActivo ? "ACTIVO ✓" : "INACTIVO ✗")}";
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // MÉTODOS ORIGINALES (Compatibilidad con Drones)
    // ═══════════════════════════════════════════════════════════
    
    public void MostrarAnalisis(PlantaData planta, int idDron)
    {
        if (planta == null) return;
        
        totalAnalizadas++;
        string estado = planta.tienePlaga ? "⚠ INFECTADA" : "✓ SANA";
        Color color = planta.tienePlaga ? Color.red : Color.green;
        
        // Detectar estrés hídrico
        if (planta.humedad < 30f)
        {
            estado = "⚠ SECA";
            color = new Color(1f, 0.5f, 0f); // Naranja
        }
        
        if (textoEstadoGeneral != null)
        {
            textoEstadoGeneral.text = $"═══ MONITOREO EN VIVO ═══\n" +
                $"Dron: #{idDron}\n" +
                $"Planta: {planta.nombreComun}\n" +
                $"Madurez: {planta.nivelMaduracion:F1}/10\n" +
                $"Estado: {estado}\n" +
                $"Humedad: {planta.humedad:F0}% 💧\n" +
                $"Salud: {planta.saludGeneral:F0}%\n" +
                $"Riegos recibidos: {planta.vecesRegada}\n" +
                $"─────────────────\n" +
                $"Total Analizadas: {totalAnalizadas}";
            textoEstadoGeneral.color = color;
        }
    }
    
    public void RegistrarAlerta(PlantaData planta, int idDron)
    {
        RegistrarAlerta(planta, idDron, "🐛 Plaga detectada");
    }
    
    public void RegistrarAlerta(PlantaData planta, int idDron, string mensajeAlerta)
    {
        if (planta == null) return;
        
        totalAlertas++;
        
        if (textoAlertas != null)
        {
            string dronInfo = idDron >= 0 ? $"Dron #{idDron}" : "Agente Riego";
            
            textoAlertas.text = $"🚨 ALERTA DETECTADA 🚨\n" +
                $"{mensajeAlerta}\n" +
                $"Planta: {planta.nombreComun}\n" +
                $"Detectado por: {dronInfo}\n" +
                $"Humedad: {planta.humedad:F0}%\n" +
                $"Coordenadas: ({planta.transform.position.x:F1}, {planta.transform.position.z:F1})\n" +
                $"─────────────────\n" +
                $"Total Alertas: {totalAlertas}";
            
            // Color según tipo de alerta
            if (mensajeAlerta.Contains("plaga") || mensajeAlerta.Contains("🐛"))
                textoAlertas.color = Color.red;
            else if (mensajeAlerta.Contains("cosechar") || mensajeAlerta.Contains("🌾"))
                textoAlertas.color = Color.yellow;
            else if (mensajeAlerta.Contains("verde") || mensajeAlerta.Contains("🥬"))
                textoAlertas.color = Color.green;
            else if (mensajeAlerta.Contains("RIEGO") || mensajeAlerta.Contains("💧"))
                textoAlertas.color = Color.cyan;
            else
                textoAlertas.color = Color.white;
        }
        
        if (idDron >= 0)
        {
            AgregarHistorial($"[ALERTA] Dron {idDron}: {mensajeAlerta} → {planta.nombreComun}");
        }
    }
    
    public void RegistrarAccion(string accion, PlantaData planta, int idDron)
    {
        if (planta == null) return;
        
        string mensaje = $"[DRON {idDron}] {accion}: {planta.nombreComun}";
        AgregarHistorial(mensaje);
        
        if (accion.Contains("Cosechando") || accion.Contains("🌾"))
            totalCosechadas++;
    }
    
    void AgregarHistorial(string mensaje)
    {
        historialAcciones.Enqueue($"[{System.DateTime.Now:HH:mm:ss}] {mensaje}");
        
        if (historialAcciones.Count > maxLineasHistorial)
            historialAcciones.Dequeue();
        
        ActualizarHistorial();
    }
    
    void ActualizarHistorial()
    {
        if (textoHistorial != null)
        {
            textoHistorial.text = "═══ HISTORIAL ═══\n" + string.Join("\n", historialAcciones);
        }
    }
    
    void ActualizarUI()
    {
        if (sistemaInicializado)
        {
            MostrarPoliticas();
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // CONTROLES PÚBLICOS DEL AGENTE
    // ═══════════════════════════════════════════════════════════
    
    /// <summary>
    /// Activa o desactiva el agente de riego
    /// </summary>
    public void ToggleRiegoAutomatico()
    {
        riegoAutomaticoActivo = !riegoAutomaticoActivo;
        MostrarPoliticas();
        
        string estado = riegoAutomaticoActivo ? "ACTIVADO" : "DESACTIVADO";
        AgregarHistorial($"[SISTEMA] Agente de riego {estado}");
    }
    
    /// <summary>
    /// Fuerza un análisis inmediato del campo
    /// </summary>
    public void ForzarAnalisisRiego()
    {
        if (!sistemaInicializado)
        {
            Debug.LogWarning("[AGENTE RIEGO] Sistema no inicializado aún");
            return;
        }
        
        AgregarHistorial($"[SISTEMA] Análisis de riego forzado manualmente");
        EjecutarPoliticasDeRiego();
    }
}