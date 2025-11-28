using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class AgenteManager : MonoBehaviour
{
    public static AgenteManager Instance { get; private set; }

    [Header("Referencias")]
    public List<AgenteFisico> drones = new List<AgenteFisico>();
    public UIController uiController;

    [Header("Configuración de Misión")]
    public float delayInicioSegundos = 0.5f;

    [Header("Tags de Plantas por Dron")]
    [Tooltip("Asigna estos tags a tus plantas: PlantaDron0, PlantaDron1, PlantaDron2, PlantaDron3")]
    public bool usarSistemaDeTags = true;

    private List<PlantaData> todasLasPlantas = new List<PlantaData>();
    private Dictionary<PlantaData, AgenteFisico> plantasAsignadas = new Dictionary<PlantaData, AgenteFisico>();

    // Estadísticas globales
    private Dictionary<int, ReporteDron> reportesDrones = new Dictionary<int, ReporteDron>();
    private int totalPlantasAnalizadas = 0;
    private int totalPlagasDetectadas = 0;
    private int totalCosechadas = 0;
    private bool misionInicializada = false;

    void Awake()
    {
        AgenteManager[] managers = FindObjectsOfType<AgenteManager>();
        if (managers.Length > 1)
        {
            Debug.LogError($"[MANAGER] ❌ ERROR CRÍTICO: {managers.Length} instancias de AgenteManager detectadas.");
            foreach (var manager in managers)
            {
                Debug.LogError($"  - {manager.gameObject.name}", manager.gameObject);
            }
        }

        if (Instance == null)
        {
            Instance = this;
            Debug.Log($"[MANAGER] ✓ AgenteManager inicializado en: {gameObject.name}");
        }
        else
        {
            Debug.LogWarning($"[MANAGER] ⚠️ Duplicado encontrado, destruyendo: {gameObject.name}");
            Destroy(gameObject);
            return;
        }
    }

    void Start()
    {
        StartCoroutine(InicializarMisionConDelay());
    }

    IEnumerator InicializarMisionConDelay()
    {
        yield return new WaitForSeconds(delayInicioSegundos);
        InicializarMision();
    }

    void InicializarMision()
    {
        Debug.Log("[MANAGER] 🚀 Iniciando misión...");

        todasLasPlantas = FindObjectsOfType<PlantaData>().ToList();

        if (todasLasPlantas.Count == 0)
        {
            Debug.LogError("[MANAGER] ❌ No se detectaron plantas en escena.");
            return;
        }

        Debug.Log($"[MANAGER] 🌱 {todasLasPlantas.Count} plantas detectadas.");

        if (uiController == null)
        {
            uiController = FindObjectOfType<UIController>();
            if (uiController != null)
            {
                Debug.Log("[MANAGER] ✓ UIController encontrado automáticamente");
            }
        }

        if (drones.Count == 0)
        {
            Debug.LogError("[MANAGER] ❌ No hay drones asignados!");
            return;
        }

        Debug.Log($"[MANAGER] ✓ {drones.Count} drones listos para operar");

        // Inicializar reportes
        for (int i = 0; i < drones.Count; i++)
        {
            if (drones[i] != null)
            {
                reportesDrones[i] = new ReporteDron(i);
            }
            else
            {
                Debug.LogError($"[MANAGER] ❌ Dron en índice {i} es NULL!");
            }
        }

        // Ajustar rotación inicial hacia la primera planta
        AjustarRotacionesIniciales();

        // Asignar plantas según el sistema elegido
        if (usarSistemaDeTags)
        {
            AsignarPlantasPorTags();
        }
        else
        {
            AsignarPlantasPorProximidad();
        }

        misionInicializada = true;
        Debug.Log("[MANAGER] ✓ Misión inicializada completamente");
    }

    void AjustarRotacionesIniciales()
    {
        for (int i = 0; i < drones.Count; i++)
        {
            if (drones[i] == null) continue;

            var plantaCercana = todasLasPlantas
                .OrderBy(p => Vector3.Distance(drones[i].transform.position, p.transform.position))
                .FirstOrDefault();

            if (plantaCercana != null)
            {
                Vector3 dir = plantaCercana.transform.position - drones[i].transform.position;
                dir.y = 0;
                if (dir != Vector3.zero)
                {
                    drones[i].transform.rotation = Quaternion.LookRotation(dir);
                }
            }
        }
    }

    // ═══════════════════════════════════════════════════════════
    // SISTEMA DE ASIGNACIÓN POR TAGS
    // ═══════════════════════════════════════════════════════════
    void AsignarPlantasPorTags()
    {
        Debug.Log("[MANAGER] 📋 Usando sistema de asignación por TAGS");

        for (int i = 0; i < drones.Count; i++)
        {
            if (drones[i] == null) continue;

            string tagBuscado = $"Tomato{i+1}";
            
            // Buscar todas las plantas con el tag específico
            GameObject[] plantasGO = GameObject.FindGameObjectsWithTag(tagBuscado);
            List<PlantaData> plantasDelDron = new List<PlantaData>();

            foreach (var go in plantasGO)
            {
                PlantaData planta = go.GetComponent<PlantaData>();
                if (planta != null)
                {
                    plantasDelDron.Add(planta);
                }
            }

            if (plantasDelDron.Count == 0)
            {
                Debug.LogWarning($"[MANAGER] ⚠️ No se encontraron plantas con tag '{tagBuscado}' para Dron {i}");
                continue;
            }

            // Ordenar plantas por distancia al dron (ruta óptima)
            var plantasOrdenadas = plantasDelDron
                .OrderBy(p => Vector3.Distance(drones[i].transform.position, p.transform.position))
                .ToList();

            // Asignar ruta al dron
            drones[i].AsignarRuta(plantasOrdenadas, i);

            // Registrar asignaciones
            foreach (var planta in plantasOrdenadas)
            {
                if (!plantasAsignadas.ContainsKey(planta))
                {
                    plantasAsignadas.Add(planta, drones[i]);
                }
            }

            Debug.Log($"[MANAGER] 🚁 Dron {i} → {plantasOrdenadas.Count} plantas con tag '{tagBuscado}'");
        }

        Debug.Log("[MANAGER] ✔ Asignación por tags COMPLETADA");
    }

    // ═══════════════════════════════════════════════════════════
    // SISTEMA DE ASIGNACIÓN POR PROXIMIDAD (ALTERNATIVO)
    // ═══════════════════════════════════════════════════════════
    void AsignarPlantasPorProximidad()
    {
        Debug.Log("[MANAGER] 📋 Usando sistema de asignación por PROXIMIDAD");

        int plantasPorDron = Mathf.CeilToInt((float)todasLasPlantas.Count / drones.Count);
        Debug.Log($"[MANAGER] Distribuyendo ~{plantasPorDron} plantas por dron");

        List<PlantaData> plantasDisponibles = new List<PlantaData>(todasLasPlantas);

        for (int i = 0; i < drones.Count; i++)
        {
            if (drones[i] == null || plantasDisponibles.Count == 0) continue;

            List<PlantaData> rutaDron = new List<PlantaData>();
            Vector3 posicionActual = drones[i].transform.position;

            // Asignar plantas cercanas al dron
            for (int j = 0; j < plantasPorDron && plantasDisponibles.Count > 0; j++)
            {
                var plantaCercana = plantasDisponibles
                    .OrderBy(p => Vector3.Distance(posicionActual, p.transform.position))
                    .First();

                rutaDron.Add(plantaCercana);
                plantasDisponibles.Remove(plantaCercana);
                posicionActual = plantaCercana.transform.position;
            }

            drones[i].AsignarRuta(rutaDron, i);

            foreach (var planta in rutaDron)
            {
                if (!plantasAsignadas.ContainsKey(planta))
                {
                    plantasAsignadas.Add(planta, drones[i]);
                }
            }

            Debug.Log($"[MANAGER] 🚁 Dron {i} → {rutaDron.Count} plantas por proximidad");
        }

        Debug.Log("[MANAGER] ✔ Asignación por proximidad COMPLETADA");
    }

    // ════════════════════════════════════════════════════════════
    // NOTIFICACIONES DE ANÁLISIS
    // ════════════════════════════════════════════════════════════

    public void NotificarAnalisis(PlantaData planta, int idDron)
    {
        if (!misionInicializada || planta == null) return;

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarAnalisis(planta);
        }

        totalPlantasAnalizadas++;

        if (uiController != null)
        {
            uiController.MostrarAnalisis(planta, idDron);
        }

        // Registrar alertas específicas
        if (planta.EstaListaParaCosechar())
        {
            uiController?.RegistrarAlerta(planta, idDron, "🌾 Lista para cosechar");
        }

        if (planta.EstaMuyVerde())
        {
            uiController?.RegistrarAlerta(planta, idDron, "🥬 Planta muy verde");
        }

        if (planta.TienePlagaActiva())
        {
            totalPlagasDetectadas++;
            uiController?.RegistrarAlerta(planta, idDron, "🐛 Plaga detectada");
        }
    }

    public void NotificarAlerta(PlantaData planta, int idDron)
    {
        if (!misionInicializada || planta == null) return;

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarPlaga();
        }

        if (uiController != null)
        {
            uiController.RegistrarAlerta(planta, idDron);
        }
    }

    public void NotificarAccion(string accion, PlantaData planta, int idDron)
    {
        if (!misionInicializada || planta == null) return;

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarAccion(accion);
        }

        if (uiController != null)
        {
            uiController.RegistrarAccion(accion, planta, idDron);
        }
    }

    public void NotificarMisionCompleta(int idDron, int plantasAnalizadas, int plagasDetectadas, int cosechadas)
    {
        if (!misionInicializada) return;

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].MisionCompleta(plantasAnalizadas, plagasDetectadas, cosechadas);
        }

        totalCosechadas += cosechadas;

        Debug.Log($"[MANAGER] ✓ Dron {idDron} completó su misión");

        // Verificar si todos terminaron
        bool todosProcesados = reportesDrones.Values.All(r => r.misionCompleta);

        if (todosProcesados)
        {
            MostrarReporteFinal();
        }
    }

    // ════════════════════════════════════════════════════════════
    // REPORTES Y ESTADÍSTICAS
    // ════════════════════════════════════════════════════════════

    void MostrarReporteFinal()
    {
        Debug.Log("════════════════════════════════════════════════════════════");
        Debug.Log("                  📊 REPORTE FINAL DE MISIÓN");
        Debug.Log("════════════════════════════════════════════════════════════");
        Debug.Log($"Total de plantas analizadas: {totalPlantasAnalizadas}/{todasLasPlantas.Count}");
        Debug.Log($"Total de plagas detectadas: {totalPlagasDetectadas}");
        Debug.Log($"Total de plantas cosechadas: {totalCosechadas}");
        Debug.Log("────────────────────────────────────────────────────────────");

        foreach (var reporte in reportesDrones.Values.OrderBy(r => r.idDron))
        {
            Debug.Log($"\n🚁 DRON {reporte.idDron}:");
            Debug.Log($"   Plantas analizadas: {reporte.plantasAnalizadas}");
            Debug.Log($"   Plagas detectadas: {reporte.plagasDetectadas}");
            Debug.Log($"   Plantas cosechadas: {reporte.plantasCosechadas}");
            Debug.Log($"   Acciones realizadas: {reporte.accionesRealizadas}");
        }

        Debug.Log("\n════════════════════════════════════════════════════════════");
        Debug.Log("              ✓ TODAS LAS MISIONES COMPLETADAS");
        Debug.Log("════════════════════════════════════════════════════════════");

        MostrarEstadisticasGlobales();
    }

    public void MostrarEstadisticasGlobales()
    {
        if (todasLasPlantas.Count == 0) return;

        int total = todasLasPlantas.Count;
        int conPlaga = todasLasPlantas.Count(p => p.tienePlaga);
        int maduras = todasLasPlantas.Count(p => p.nivelMaduracion >= 8f);
        int alertas = todasLasPlantas.Count(p => p.TieneAlertasCriticas());
        float saludProm = todasLasPlantas.Average(p => p.saludGeneral);

        Debug.Log("\n════ ESTADÍSTICAS GLOBALES DEL CAMPO ════");
        Debug.Log($"Total plantas: {total}");
        Debug.Log($"Plantas con plaga: {conPlaga} ({(float)conPlaga / total * 100:F1}%)");
        Debug.Log($"Plantas maduras: {maduras} ({(float)maduras / total * 100:F1}%)");
        Debug.Log($"Alertas IoT críticas: {alertas}");
        Debug.Log($"Salud promedio del campo: {saludProm:F1}%");
        Debug.Log("═════════════════════════════════════════");
    }

    void OnDestroy()
    {
        if (Instance == this)
        {
            Instance = null;
        }
    }
}

// ════════════════════════════════════════════════════════════
// CLASE DE REPORTE POR DRON
// ════════════════════════════════════════════════════════════
[System.Serializable]
public class ReporteDron
{
    public int idDron;
    public int plantasAnalizadas;
    public int plagasDetectadas;
    public int plantasCosechadas;
    public int accionesRealizadas;
    public bool misionCompleta;

    public ReporteDron(int id)
    {
        idDron = id;
        plantasAnalizadas = 0;
        plagasDetectadas = 0;
        plantasCosechadas = 0;
        accionesRealizadas = 0;
        misionCompleta = false;
    }

    public void RegistrarAnalisis(PlantaData planta)
    {
        // El análisis ya se cuenta en NotificarAnalisis
    }

    public void RegistrarPlaga()
    {
        plagasDetectadas++;
    }

    public void RegistrarAccion(string accion)
    {
        accionesRealizadas++;
    }

    public void MisionCompleta(int analizadas, int plagas, int cosechadas)
    {
        plantasAnalizadas = analizadas;
        plagasDetectadas = plagas;
        plantasCosechadas = cosechadas;
        misionCompleta = true;
    }
}