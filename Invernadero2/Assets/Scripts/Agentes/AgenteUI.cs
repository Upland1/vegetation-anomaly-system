using UnityEngine;
using TMPro;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI; 

public class UIController : MonoBehaviour
{
    [Header("1. Referencias UI Visuales")]
    public TextMeshProUGUI textoMonitorIzq;   
    public TextMeshProUGUI textoAlertasCentro;
    public TextMeshProUGUI textoHistorialDer; 
    public TextMeshProUGUI textoStatsArriba;  
    
    public TextMeshProUGUI textoPoliticasAgente; 
    
    [Header("2. Configuración del Mapa/Radar")]
    public RectTransform mapaRect;      
    public RectTransform indicadorPunto; 
    public Vector2 tamanoTerrenoMundo = new Vector2(100f, 100f); 
    
    [Header("3. Configuración General UI")]
    public int maxLineasHistorial = 12;
    public float tiempoBorradoAlerta = 4f; 

    [Header("4. Políticas de Riego (Sistema Central)")]
    public bool riegoAutomaticoActivo = true;
    
    [Range(0, 50)] public float umbralRiegoUrgente = 30f;
    
    [Range(30, 70)] public float umbralRiegoPreventivo = 50f;
    
    public float cantidadAguaPorRiego = 40f;
    public float intervaloAnalisis = 3f;

    private string colVerde = "#4CFF00";
    private string colRojo = "#FF3333";
    private string colAmarillo = "#FFD700";
    private string colAzul = "#00FFFF";
    private string colGris = "#AAAAAA";

    private Queue<string> historial = new Queue<string>();
    private Coroutine rutinaAlerta;

    private List<PlantaData> todasLasPlantas = new List<PlantaData>();
    private float tiempoDesdeUltimoAnalisis = 0f;
    private bool sistemaInicializado = false;

    private int totalAnalisis = 0;
    private int totalPlagas = 0;
    private int totalRiegos = 0;
    private int totalRiegosUrgentes = 0;
    private int totalRiegosPreventivos = 0;
    private int totalCosechadas = 0;

    void Start()
    {
        if(textoMonitorIzq) textoMonitorIzq.text = "Esperando conexion...";
        if(textoAlertasCentro) textoAlertasCentro.text = "";
        if(indicadorPunto != null) indicadorPunto.gameObject.SetActive(false);

        ActualizarStatsGlobales();
        AgregarHistorial("SISTEMA CENTRAL INICIADO", "INFO");

        if (todasLasPlantas.Count == 0)
        {
            Invoke(nameof(BuscarPlantasManualmente), 1f);
        }
    }

    void Update()
    {
        if (!riegoAutomaticoActivo || !sistemaInicializado) return;
        
        tiempoDesdeUltimoAnalisis += Time.deltaTime;
        
        if (tiempoDesdeUltimoAnalisis >= intervaloAnalisis)
        {
            tiempoDesdeUltimoAnalisis = 0f;
            EjecutarPoliticasDeRiego();
        }
    }

    public void MostrarAnalisis(PlantaData planta, int idDron)
    {
        if (planta == null || textoMonitorIzq == null) return;
        
        totalAnalisis++;

        // CORRECCIÓN ICONOS: Usamos [!] y [OK] en lugar de símbolos raros
        string estadoIcono = planta.tienePlaga ? "[!]" : "[OK]";
        string colorEstado = planta.tienePlaga ? colRojo : colVerde;
        string estadoTexto = planta.tienePlaga ? "INFECTADA" : "SALUDABLE";

        int numeroDronVisible = idDron + 1;
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

    public void RegistrarAlerta(PlantaData planta, int idDron, string mensajeCustom = "")
    {
        totalPlagas++;
        string mensaje = mensajeCustom == "" ? "PLAGA DETECTADA" : mensajeCustom;
        
        string detector = (idDron == -1) ? "SENSOR AUTOMATICO" : $"Dron #{idDron + 1}";

        string textoUbicacion = $"({planta.transform.position.x:F1}, {planta.transform.position.z:F1})";

        if (textoAlertasCentro != null)
        {
            if (rutinaAlerta != null) StopCoroutine(rutinaAlerta);
            rutinaAlerta = StartCoroutine(MostrarAlertaAnimada(textoUbicacion, mensaje, detector));
        }

        if (mapaRect != null && indicadorPunto != null)
        {
            ActualizarPuntoEnMapa(planta.transform.position);
        }

        // CORRECCIÓN HISTORIAL: Ahora muestra coordenadas en lugar del nombre del tomate
        AgregarHistorial($"{detector}: {mensaje} {textoUbicacion}", "ALERTA");
        
        ActualizarStatsGlobales();
    }

    IEnumerator MostrarAlertaAnimada(string lugar, string tipo, string detector)
    {
        // CORRECCIÓN ICONOS: [!] en lugar de triangulo de alerta
        textoAlertasCentro.text = 
            $"<size=150%><color={colRojo}><b>[!] ALERTA DEL SISTEMA [!]</b></color></size>\n" +
            $"<size=120%>{tipo}</size>\n" +
            $"<color={colAmarillo}>Fuente: {detector}</color>\n" +
            $"<color=white>Ubicacion: {lugar}</color>";

        yield return new WaitForSeconds(tiempoBorradoAlerta);
        textoAlertasCentro.text = "";
    }

    void ActualizarPuntoEnMapa(Vector3 posicionMundo)
    {
        indicadorPunto.gameObject.SetActive(true);
        float normX = (posicionMundo.x / tamanoTerrenoMundo.x) + 0.5f;
        float normY = (posicionMundo.z / tamanoTerrenoMundo.y) + 0.5f;
        normX = Mathf.Clamp01(normX);
        normY = Mathf.Clamp01(normY);

        Vector2 posicionUI = new Vector2(
            (normX * mapaRect.rect.width) - (mapaRect.rect.width * 0.5f),
            (normY * mapaRect.rect.height) - (mapaRect.rect.height * 0.5f)
        );
        indicadorPunto.anchoredPosition = posicionUI;
    }

    void EjecutarPoliticasDeRiego()
    {
        todasLasPlantas.RemoveAll(p => p == null);
        if (todasLasPlantas.Count == 0) return;

        int regadasEsteCiclo = 0;
        int maxRiegosPreventivos = 3; 

        var plantasOrdenadas = todasLasPlantas.OrderBy(p => p.humedad).ToList();

        foreach (var planta in plantasOrdenadas)
        {
            if (planta.humedad <= 0 || !planta.gameObject.activeSelf) continue;

            if (planta.humedad < umbralRiegoUrgente)
            {
                RegarPlanta(planta, true);
                regadasEsteCiclo++;
                RegistrarAlerta(planta, -1, "RIEGO DE EMERGENCIA");
            }
            else if (planta.humedad < umbralRiegoPreventivo && regadasEsteCiclo < maxRiegosPreventivos)
            {
                RegarPlanta(planta, false);
                regadasEsteCiclo++;
                
                string ubic = $"({planta.transform.position.x:F1}, {planta.transform.position.z:F1})";
                AgregarHistorial($"Riego preventivo en {ubic}", "INFO");
            }
            
            planta.humedad -= 0.5f; 
        }

        if (regadasEsteCiclo > 0) ActualizarStatsGlobales();
        MostrarPoliticasEnUI();
    }

    void RegarPlanta(PlantaData planta, bool esUrgente)
    {
        planta.Regar(cantidadAguaPorRiego);

        totalRiegos++;
        if (esUrgente) totalRiegosUrgentes++;
        else totalRiegosPreventivos++;
    }

    void BuscarPlantasManualmente()
    {
        todasLasPlantas = FindObjectsOfType<PlantaData>().ToList();
        if (todasLasPlantas.Count > 0)
        {
            sistemaInicializado = true;
            AgregarHistorial($"[SISTEMA] {todasLasPlantas.Count} plantas conectadas", "INFO");
        }
    }

    public void RegistrarAccion(string accion, PlantaData planta, int idDron)
    {
        int numeroDronVisible = idDron + 1;
        // Mantenemos el nombre aquí para acciones normales, a menos que quieras coordenadas también
        AgregarHistorial($"Dron #{numeroDronVisible}: {accion} ({planta.nombreComun})", "INFO");
        
        if (accion.Contains("Cosechando")) totalCosechadas++;
    }

    void AgregarHistorial(string mensaje, string tipo)
    {
        string hora = System.DateTime.Now.ToString("HH:mm:ss");
        string colorLog = tipo == "ALERTA" ? colRojo : colVerde;
        
        // CORRECCIÓN ICONOS: X y -> son seguros
        string icono = tipo == "ALERTA" ? "X" : "->"; 

        string linea = $"<color={colGris}>[{hora}]</color> <color={colorLog}>{icono}</color> {mensaje}";
        
        historial.Enqueue(linea);
        if (historial.Count > maxLineasHistorial) historial.Dequeue();

        if (textoHistorialDer != null)
        {
            textoHistorialDer.text = "<b><size=110%>Historial de Actividad</size></b>\n" + string.Join("\n", historial);
        }
    }

    void ActualizarStatsGlobales()
    {
        if (textoStatsArriba != null)
        {
            textoStatsArriba.text = 
                $"<color={colVerde}>ANALISIS: <b>{totalAnalisis}</b></color>        " +
                $"<color={colRojo}>PLAGAS: <b>{totalPlagas}</b></color>       " +
                $"<color={colAzul}>RIEGOS: <b>{totalRiegos}</b></color>        ";
        }
    }

    void MostrarPoliticasEnUI()
    {
        if (textoPoliticasAgente != null)
        {
            textoPoliticasAgente.text = $"SISTEMA RIEGO: {(riegoAutomaticoActivo ? "ON" : "OFF")}\n" +
                                        $"Urgentes: {totalRiegosUrgentes} | Preventivos: {totalRiegosPreventivos}";
        }
    }

    public void InicializarConPlantas(List<PlantaData> p) 
    { 
        todasLasPlantas = p;
        sistemaInicializado = true;
        ActualizarStatsGlobales(); 
    }
}