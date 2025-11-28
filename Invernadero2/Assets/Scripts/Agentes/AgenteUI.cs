using UnityEngine;
using TMPro;
using System.Collections.Generic;

public class UIController : MonoBehaviour
{
    [Header("Referencias UI")]
    public TextMeshProUGUI textoEstadoGeneral;
    public TextMeshProUGUI textoAlertas;
    public TextMeshProUGUI textoHistorial;
    
    [Header("Configuración")]
    public int maxLineasHistorial = 10;
    
    private int totalAlertas = 0;
    private int totalAnalizadas = 0;
    private int totalCosechadas = 0;
    private Queue<string> historialAcciones = new Queue<string>();
    
    void Start()
    {
        ActualizarUI();
    }
    
    public void MostrarAnalisis(PlantaData planta, int idDron)
    {
        totalAnalizadas++;
        string estado = planta.tienePlaga ? "⚠ INFECTADA" : "✓ SANA";
        Color color = planta.tienePlaga ? Color.red : Color.green;
        
        if (textoEstadoGeneral != null)
        {
            textoEstadoGeneral.text = $"═══ MONITOREO EN VIVO ═══\n" +
                $"Dron: #{idDron}\n" +
                $"Planta: {planta.nombreComun}\n" +
                $"Madurez: {planta.nivelMaduracion:F1}/10\n" +
                $"Estado: {estado}\n" +
                $"Humedad: {planta.humedad:F0}%\n" +
                $"Salud: {planta.saludGeneral:F0}%\n" +
                $"─────────────────\n" +
                $"Total Analizadas: {totalAnalizadas}";
            textoEstadoGeneral.color = color;
        }
    }
    
    // ══════════════════════════════════════════════════════════════
    // SOBRECARGA DE MÉTODOS: Acepta 2 o 3 parámetros
    // ══════════════════════════════════════════════════════════════
    
    /// <summary>
    /// Registra alerta genérica de plaga (2 parámetros)
    /// </summary>
    public void RegistrarAlerta(PlantaData planta, int idDron)
    {
        RegistrarAlerta(planta, idDron, "🐛 Plaga detectada");
    }
    
    /// <summary>
    /// Registra alerta con mensaje personalizado (3 parámetros)
    /// ✅ Este es el método principal llamado por NotificarAnalisis()
    /// </summary>
    public void RegistrarAlerta(PlantaData planta, int idDron, string mensajeAlerta)
    {
        totalAlertas++;
        
        if (textoAlertas != null)
        {
            textoAlertas.text = $"🚨 ALERTA DETECTADA 🚨\n" +
                $"{mensajeAlerta}\n" +
                $"Planta: {planta.nombreComun}\n" +
                $"Detectado por: Dron #{idDron}\n" +
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
            else
                textoAlertas.color = Color.white;
        }
        
        AgregarHistorial($"[ALERTA] Dron {idDron}: {mensajeAlerta} → {planta.nombreComun}");
    }
    
    public void RegistrarAccion(string accion, PlantaData planta, int idDron)
    {
        string mensaje = $"[DRON {idDron}] {accion}: {planta.nombreComun}";
        AgregarHistorial(mensaje);
        
        if (accion.Contains("Cosechando"))
            totalCosechadas++;
    }
    
    void AgregarHistorial(string mensaje)
    {
        historialAcciones.Enqueue($"[{System.DateTime.Now:HH:mm:ss}] {mensaje}");
        
        // Limitar tamaño del historial
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
        // Actualizar estadísticas generales si es necesario
    }
}