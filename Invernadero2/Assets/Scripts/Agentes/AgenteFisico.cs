using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class AgenteFisico : MonoBehaviour
{
    [Header("Configuración Vuelo")]
    public float velocidad = 3.0f;
    public float alturaVuelo = 1.5f;
    public float distanciaParaParar = 0.5f;

    [Header("Configuración Análisis")]
    public float tiempoAnalisis = 2.0f;
    public Transform puntoSensor;

    [Header("Configuración Surcos")]
    public string surcoAsignado = "";
    public float desplazamientoLateral = 1.0f;
    public float suavizadoRotacion = 6f;

    [Header("Cosecha y Acciones")]
    public float nivelMadurezCosecha = 8f;
    public float tiempoAplicacionPesticida = 1.5f;

    // Estado interno
    private List<PlantaData> ruta = new List<PlantaData>();
    private int indiceActual = 0;
    private int idDron = 0;
    private bool rutaActiva = false;
    private bool analizando = false;

    // Estadísticas del análisis
    private int plantasAnalizadas = 0;
    private int plagasDetectadas = 0;
    private int plantasCosechadas = 0;

    private Transform surcoTransform;
    private Vector3 direccionSurco;
    private Vector3 lateralSurco;
    private float largoSurco;
    private Vector3 inicioSurco;
    private Vector3 finSurco;

    private Material materialDron;
    private Color colorOriginal;

    void Start()
    {
        Vector3 e = transform.rotation.eulerAngles;
        transform.rotation = Quaternion.Euler(0, e.y, 0);

        Renderer r = GetComponent<Renderer>();
        if (r != null)
        {
            materialDron = r.material;
            colorOriginal = materialDron.color;
        }

        // Validar que AgenteManager existe
        if (AgenteManager.Instance == null)
        {
            Debug.LogError($"[DRON {idDron}] ⚠️ AgenteManager.Instance es NULL! Asegúrate de que exista un AgenteManager en la escena.");
        }
    }

    public void AsignarRuta(List<PlantaData> plantas, int id)
    {
        ruta = plantas;
        idDron = id;

        string[] nombresSurcos = { "Surco1", "Surco2", "Surco3", "Surco4" };
        surcoAsignado = nombresSurcos[id % nombresSurcos.Length];

        GameObject surcoGO = GameObject.FindGameObjectWithTag(surcoAsignado);

        if (surcoGO != null)
        {
            surcoTransform = surcoGO.transform;

            CapsuleCollider capsule = surcoGO.GetComponent<CapsuleCollider>();
            if (capsule != null)
            {
                largoSurco = capsule.height * surcoTransform.lossyScale.y;
            }
            else
            {
                largoSurco = surcoTransform.lossyScale.y * 2f;
            }

            direccionSurco = surcoTransform.up;
            direccionSurco.Normalize();

            Vector3 centroSurco = surcoTransform.position;
            inicioSurco = centroSurco - direccionSurco * (largoSurco / 2f);
            finSurco = centroSurco + direccionSurco * (largoSurco / 2f);

            lateralSurco = Vector3.Cross(Vector3.up, direccionSurco).normalized;

            Vector3 mirarDerecha = -lateralSurco;
            transform.rotation = Quaternion.LookRotation(mirarDerecha, Vector3.up);

            Debug.Log($"[DRON {idDron}] Surco detectado: Largo={largoSurco:F2}u, Inicio={inicioSurco}, Fin={finSurco}");
        }

        if (materialDron != null)
        {
            Color[] colores = { Color.blue, Color.green, Color.yellow, Color.magenta };
            materialDron.color = colores[id % colores.Length];
            colorOriginal = materialDron.color;
        }

        rutaActiva = true;
        indiceActual = 0;

        Debug.Log($"[DRON {idDron}] Ruta asignada ({ruta.Count} plantas), Surco: {surcoAsignado}");
    }

    void Update()
    {
        if (!rutaActiva || analizando || ruta.Count == 0)
            return;

        if (indiceActual >= ruta.Count)
        {
            rutaActiva = false;
            MisionCompletada();
            return;
        }

        PlantaData objetivo = ruta[indiceActual];
        Vector3 destino = CalcularDestinoSurco(objetivo);

        transform.position = Vector3.MoveTowards(
            transform.position,
            destino,
            velocidad * Time.deltaTime
        );

        Quaternion rotDeseada = Quaternion.LookRotation(-lateralSurco, Vector3.up);
        transform.rotation = Quaternion.Slerp(transform.rotation, rotDeseada, suavizadoRotacion * Time.deltaTime);

        float dist = Vector2.Distance(
            new Vector2(transform.position.x, transform.position.z),
            new Vector2(destino.x, destino.z)
        );

        if (dist < distanciaParaParar)
        {
            StartCoroutine(AnalizarPlantaCompleta(objetivo));
        }
    }

    Vector3 CalcularDestinoSurco(PlantaData planta)
    {
        Vector3 plantaPos = planta.transform.position;

        Vector3 relativo = plantaPos - inicioSurco;
        float distanciaProyectada = Vector3.Dot(relativo, direccionSurco);
        distanciaProyectada = Mathf.Clamp(distanciaProyectada, 0, largoSurco);

        Vector3 puntoEnSurco = inicioSurco + direccionSurco * distanciaProyectada;
        puntoEnSurco += lateralSurco * desplazamientoLateral;
        puntoEnSurco.y = plantaPos.y + alturaVuelo;

        return puntoEnSurco;
    }

    // ============================================================
    // ANÁLISIS COMPLETO DE LA PLANTA
    // ============================================================
    IEnumerator AnalizarPlantaCompleta(PlantaData planta)
    {
        analizando = true;
        
        if (materialDron != null)
        {
            materialDron.color = Color.cyan;
        }

        // Dibujar láser de escaneo
        if (puntoSensor != null)
        {
            Debug.DrawLine(puntoSensor.position, planta.transform.position, Color.cyan, tiempoAnalisis);
        }

        Debug.Log($"[DRON {idDron}] 🔍 Iniciando análisis de {planta.nombreComun}...");

        // Tiempo de escaneo
        yield return new WaitForSeconds(tiempoAnalisis);

        // ─────────── DETECCIÓN INMEDIATA DE PLAGA ───────────
        if (planta.tienePlaga)
        {
            plagasDetectadas++;
            planta.MarcarComoEnferma();
            
            // Alerta inmediata (con validación)
            if (AgenteManager.Instance != null)
            {
                AgenteManager.Instance.NotificarAlerta(planta, idDron);
            }
            else
            {
                Debug.LogWarning($"[DRON {idDron}] No se pudo notificar alerta - AgenteManager no disponible");
            }
            
            Debug.Log($"[DRON {idDron}] 🐛 ¡PLAGA DETECTADA en {planta.nombreComun}!");
        }
        else
        {
            planta.MarcarComoSana();
        }

        // ─────────── ANÁLISIS COMPLETO ───────────
        string estadoSalud = planta.tienePlaga ? "INFECTADA" : "SANA";
        string estadoMadurez = ObtenerEstadoMadurez(planta.nivelMaduracion);

        // Enviar análisis completo al manager (con validación)
        if (AgenteManager.Instance != null)
        {
            AgenteManager.Instance.NotificarAnalisis(planta, idDron);
        }

        Debug.Log($"[DRON {idDron}] 📊 ANÁLISIS COMPLETO:\n" +
                  $"  Planta: {planta.nombreComun}\n" +
                  $"  Salud: {estadoSalud}\n" +
                  $"  Madurez: {planta.nivelMaduracion:F1}/10 ({estadoMadurez})\n" +
                  $"  Salud General: {planta.saludGeneral:F1}%");

        // ─────────── EJECUTAR ACCIONES SEGÚN ANÁLISIS ───────────
        yield return StartCoroutine(EjecutarAccionesPostAnalisis(planta));

        // Marcar como analizada
        planta.yaAnalizada = true;
        plantasAnalizadas++;

        if (materialDron != null)
        {
            materialDron.color = colorOriginal;
        }
        
        analizando = false;
        indiceActual++;
    }

    IEnumerator EjecutarAccionesPostAnalisis(PlantaData planta)
    {
        // 1. Aplicar pesticida si hay plaga
        if (planta.tienePlaga)
        {
            if (materialDron != null)
            {
                materialDron.color = Color.red;
            }

            if (AgenteManager.Instance != null)
            {
                AgenteManager.Instance.NotificarAccion("Aplicando pesticida", planta, idDron);
            }
            
            Debug.Log($"[DRON {idDron}] 💉 Aplicando pesticida a {planta.nombreComun}...");
            
            yield return new WaitForSeconds(tiempoAplicacionPesticida);
            planta.MarcarComoSana();
            
            Debug.Log($"[DRON {idDron}] ✓ Pesticida aplicado exitosamente");
        }

        // 2. Evaluar cosecha
        if (planta.nivelMaduracion >= nivelMadurezCosecha)
        {
            if (materialDron != null)
            {
                materialDron.color = Color.yellow;
            }

            if (AgenteManager.Instance != null)
            {
                AgenteManager.Instance.NotificarAccion("Cosechando", planta, idDron);
            }
            
            Debug.Log($"[DRON {idDron}] 🌾 Cosechando {planta.nombreComun}...");
            
            yield return new WaitForSeconds(1f);
            plantasCosechadas++;
            
            Debug.Log($"[DRON {idDron}] ✓ Cosecha completada");
        }
        else if (planta.nivelMaduracion < 5f)
        {
            if (AgenteManager.Instance != null)
            {
                AgenteManager.Instance.NotificarAccion("Muy verde — no cosechar", planta, idDron);
            }
            Debug.Log($"[DRON {idDron}] 🥬 {planta.nombreComun} está muy verde, no cosechar");
        }

        yield return null;
    }

    string ObtenerEstadoMadurez(float nivel)
    {
        if (nivel >= 8f) return "Lista para cosechar";
        if (nivel >= 5f) return "En proceso";
        return "Muy verde";
    }

    void MisionCompletada()
    {
        Debug.Log($"[DRON {idDron}] ════════════════════════════════════\n" +
                  $"✓ MISIÓN FINALIZADA\n" +
                  $"Surco: {surcoAsignado}\n" +
                  $"Plantas analizadas: {plantasAnalizadas}/{ruta.Count}\n" +
                  $"Plagas detectadas: {plagasDetectadas}\n" +
                  $"Plantas cosechadas: {plantasCosechadas}\n" +
                  $"════════════════════════════════════");

        if (materialDron != null)
        {
            materialDron.color = Color.green;
        }

        // Enviar reporte final al manager (con validación)
        if (AgenteManager.Instance != null)
        {
            AgenteManager.Instance.NotificarMisionCompleta(idDron, plantasAnalizadas, plagasDetectadas, plantasCosechadas);
        }
        else
        {
            Debug.LogWarning($"[DRON {idDron}] No se pudo enviar reporte final - AgenteManager no disponible");
        }
    }
}