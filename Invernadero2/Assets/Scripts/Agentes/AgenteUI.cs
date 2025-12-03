using UnityEngine;
using TMPro;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI; // Necesario para manipular imágenes/paneles UI

public class UIController : MonoBehaviour
{
    [Header("1. Arrastra los Textos del Canvas aquí")]
    public TextMeshProUGUI textoMonitorIzq;   // Para datos del dron/planta
    public TextMeshProUGUI textoAlertasCentro;// Para alertas grandes
    public TextMeshProUGUI textoHistorialDer; // Para el log
    public TextMeshProUGUI textoStatsArriba;  // Para estadísticas globales
    
    [Header("2. Configuración del Mapa/Radar")]
    public RectTransform mapaRect;      // El panel que sirve de fondo del mapa
    public RectTransform indicadorPunto; // La imagen (punto rojo) que se moverá
    // Ajusta estos valores al tamaño real de tu terreno en Unity
    public Vector2 tamanoTerrenoMundo = new Vector2(100f, 100f); 
    
    [Header("Configuración General")]
    public int maxLineasHistorial = 12;
    public float tiempoBorradoAlerta = 4f; 

    // Colores corporativos (Hexadecimales)
    private string colVerde = "#4CFF00";
    private string colRojo = "#FF3333";
    private string colAmarillo = "#FFD700";
    private string colAzul = "#00FFFF";
    private string colGris = "#AAAAAA";

    private Queue<string> historial = new Queue<string>();
    private int totalAnalisis = 0;
    private int totalPlagas = 0;
    private Coroutine rutinaAlerta;

    void Start()
    {
        if(textoMonitorIzq) textoMonitorIzq.text = "Esperando conexion...";
        if(textoAlertasCentro) textoAlertasCentro.text = "";
        
        // Ocultar el punto del mapa al inicio si existe
        if (indicadorPunto != null) indicadorPunto.gameObject.SetActive(false);

        ActualizarStatsGlobales();
        AgregarHistorial("SISTEMA INICIADO", "INFO");
    }

    // ═══════════════════════════════════════════════════════════
    // SECCIÓN 1: MONITOR EN VIVO (Sin iconos raros)
    // ═══════════════════════════════════════════════════════════
    public void MostrarAnalisis(PlantaData planta, int idDron)
    {
        if (planta == null || textoMonitorIzq == null) return;
        
        totalAnalisis++;

        string estadoIcono = planta.tienePlaga ? "[!]" : "[OK]";
        string colorEstado = planta.tienePlaga ? colRojo : colVerde;
        string estadoTexto = planta.tienePlaga ? "INFECTADA" : "SALUDABLE";

        int numeroDronVisible = idDron + 1;

        // Formato de coordenadas más limpio (sin decimales excesivos)
        string coords = $"X:{planta.transform.position.x:F1}, Z:{planta.transform.position.z:F1}";

        string reporte = 
            $"<size=120%><color={colAzul}><b>DRON #{numeroDronVisible} - VISTA EN VIVO</b></color></size>\n" +
            $"----------------------\n" +
            $"<b>OBJETIVO:</b> <color=white>{planta.nombreComun}</color>\n" +
            $"<b>MADUREZ:</b>  <color={colAmarillo}>{planta.nivelMaduracion:F1}/10</color>\n" +
            $"<b>HUMEDAD:</b>  <color={colAzul}>{planta.humedad:F0}%</color>\n" +
            $"----------------------\n" +
            $"<b>ESTADO:</b>   <color={colorEstado}>{estadoIcono} {estadoTexto}</color>\n" +
            $"\n<size=80%><color={colGris}>Ubicacion: {coords}</color></size>";

        textoMonitorIzq.text = reporte;
        ActualizarStatsGlobales();
    }

    // ═══════════════════════════════════════════════════════════
    // SECCIÓN 2: ALERTAS CRÍTICAS Y MAPA
    // ═══════════════════════════════════════════════════════════
    public void RegistrarAlerta(PlantaData planta, int idDron, string mensajeCustom = "")
    {
        totalPlagas++;
        string mensaje = mensajeCustom == "" ? "PLAGA DETECTADA" : mensajeCustom;
        int numeroDronVisible = idDron + 1;

        // CAMBIO: Preparamos el texto de coordenadas en lugar del nombre
        string textoUbicacion = $"({planta.transform.position.x:F1}, {planta.transform.position.z:F1})";

        if (textoAlertasCentro != null)
        {
            if (rutinaAlerta != null) StopCoroutine(rutinaAlerta);
            // Pasamos las coordenadas en vez del nombre
            rutinaAlerta = StartCoroutine(MostrarAlertaAnimada(textoUbicacion, mensaje, numeroDronVisible));
        }

        // --- ACTUALIZACIÓN DEL MAPA ---
        if (mapaRect != null && indicadorPunto != null)
        {
            ActualizarPuntoEnMapa(planta.transform.position);
        }

        // Agregar al historial (aquí sí dejamos el nombre y las coordenadas para referencia completa)
        string coordsHistorial = $"({planta.transform.position.x:F0},{planta.transform.position.z:F0})";
        AgregarHistorial($"Dron #{numeroDronVisible}: {mensaje} en {planta.nombreComun} {coordsHistorial}", "ALERTA");
        
        ActualizarStatsGlobales();
    }

    // Función para mover el punto en el mapa UI
    void ActualizarPuntoEnMapa(Vector3 posicionMundo)
    {
        indicadorPunto.gameObject.SetActive(true);

        // Convertir posición del mundo (X, Z) a posición normalizada (0 a 1)
        float normX = (posicionMundo.x / tamanoTerrenoMundo.x) + 0.5f;
        float normY = (posicionMundo.z / tamanoTerrenoMundo.y) + 0.5f;

        normX = Mathf.Clamp01(normX);
        normY = Mathf.Clamp01(normY);

        float mapaAncho = mapaRect.rect.width;
        float mapaAlto = mapaRect.rect.height;

        Vector2 posicionUI = new Vector2(
            (normX * mapaAncho) - (mapaAncho * 0.5f),
            (normY * mapaAlto) - (mapaAlto * 0.5f)
        );

        indicadorPunto.anchoredPosition = posicionUI;
    }

    IEnumerator MostrarAlertaAnimada(string lugar, string tipo, int numDron)
    {
        // Alerta visual grande
        textoAlertasCentro.text = 
            $"<size=150%><color={colRojo}><b>[!] ALERTA DEL SISTEMA [!]</b></color></size>\n" +
            $"<size=120%>{tipo}</size>\n" +
            $"<color={colAmarillo}>Detectado por: Dron #{numDron}</color>\n" +
            $"<color=white>Ubicacion: {lugar}</color>";

        yield return new WaitForSeconds(tiempoBorradoAlerta);
        
        textoAlertasCentro.text = "";
    }

    // ═══════════════════════════════════════════════════════════
    // SECCIÓN 3: HISTORIAL 
    // ═══════════════════════════════════════════════════════════
    public void RegistrarAccion(string accion, PlantaData planta, int idDron)
    {
        int numeroDronVisible = idDron + 1;
        AgregarHistorial($"Dron #{numeroDronVisible}: {accion} ({planta.nombreComun})", "INFO");
    }

    void AgregarHistorial(string mensaje, string tipo)
    {
        string hora = System.DateTime.Now.ToString("HH:mm:ss");
        string colorLog = tipo == "ALERTA" ? colRojo : colVerde;
        string icono = tipo == "ALERTA" ? "X" : "->"; 

        string linea = $"<color={colGris}>[{hora}]</color> <color={colorLog}>{icono}</color> {mensaje}";
        
        historial.Enqueue(linea);
        if (historial.Count > maxLineasHistorial) historial.Dequeue();

        if (textoHistorialDer != null)
        {
            textoHistorialDer.text = "<b><size=110%>Historial de Actividad</size></b>\n" + string.Join("\n", historial);
        }
    }

    // ═══════════════════════════════════════════════════════════
    // SECCIÓN 4: ESTADÍSTICAS
    // ═══════════════════════════════════════════════════════════
    void ActualizarStatsGlobales()
    {
        if (textoStatsArriba != null)
        {
            textoStatsArriba.text = 
                $"<color={colVerde}>ANALISIS: <b>{totalAnalisis}</b></color>    |    " +
                $"<color={colRojo}>PLAGAS: <b>{totalPlagas}</b></color>    |    " +
                $"<color={colAzul}>ESTADO: <b>EN LINEA</b></color>";
        }
    }

    public void InicializarConPlantas(List<PlantaData> p) { ActualizarStatsGlobales(); }
}