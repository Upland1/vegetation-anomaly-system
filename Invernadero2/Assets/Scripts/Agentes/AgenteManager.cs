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
    [Tooltip("Asigna estos tags a tus plantas: Tomato1, Tomato2, Tomato3, Tomato4")]
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

        // Enviar plantas al UIController (Agente de Riego)
        if (uiController != null)
        {
            uiController.InicializarConPlantas(todasLasPlantas);
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
        Debug.Log("[MANAGER] 💧 Agente de Riego UIController activo");
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
            
            // Ordenar plantas por distancia al dron original (ruta óptima)
            var plantasOrdenadas = plantasDelDron
                .OrderBy(p => Vector3.Distance(drones[i].transform.position, p.transform.position))
                .ToList();
            
            // VERIFICAR DISPONIBILIDAD DEL DRON
            int dronAsignado = i;
            
            if (!DronDisponible(i))
            {
                Debug.LogWarning($"[MANAGER] ⚠️ Dron {i} NO disponible. Buscando dron alternativo...");
                dronAsignado = BuscarDronMasCercano(plantasOrdenadas[0].transform.position, i);
                
                if (dronAsignado == -1)
                {
                    Debug.LogError($"[MANAGER] ❌ No hay drones disponibles para plantas con tag '{tagBuscado}'");
                    continue;
                }
                
                Debug.Log($"[MANAGER] 🔄 Plantas reasignadas de Dron {i} → Dron {dronAsignado}");
                
                // Reordenar plantas según la posición del nuevo dron asignado
                plantasOrdenadas = plantasDelDron
                    .OrderBy(p => Vector3.Distance(drones[dronAsignado].transform.position, p.transform.position))
                    .ToList();
            }
            
            // Asignar ruta al dron disponible
            drones[dronAsignado].AsignarRuta(plantasOrdenadas, dronAsignado);
            
            // Registrar asignaciones
            foreach (var planta in plantasOrdenadas)
            {
                if (!plantasAsignadas.ContainsKey(planta))
                {
                    plantasAsignadas.Add(planta, drones[dronAsignado]);
                }
            }
            
            Debug.Log($"[MANAGER] 🚁 Dron {dronAsignado} → {plantasOrdenadas.Count} plantas con tag '{tagBuscado}'");
        }
        
        Debug.Log("[MANAGER] ✔ Asignación por tags COMPLETADA");
    }

    bool DronDisponible(int indiceDron)
    {
        if (indiceDron < 0 || indiceDron >= drones.Count || drones[indiceDron] == null)
            return false;
        
        // Aquí puedes agregar validaciones adicionales:
        // return drones[indiceDron].bateria > 20f && !drones[indiceDron].enMantenimiento;
        
        return true;
    }

    int BuscarDronMasCercano(Vector3 posicion, int excluirDron = -1)
    {
        float menorDistancia = float.MaxValue;
        int dronMasCercano = -1;
        
        for (int i = 0; i < drones.Count; i++)
        {
            if (i == excluirDron || drones[i] == null || !DronDisponible(i))
                continue;
            
            float distancia = Vector3.Distance(drones[i].transform.position, posicion);
            
            if (distancia < menorDistancia)
            {
                menorDistancia = distancia;
                dronMasCercano = i;
            }
        }
        
        return dronMasCercano;
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
        if (!misionInicializada || planta == null) 
        {
            Debug.LogWarning($"[MANAGER] ⚠️ NotificarAnalisis llamado pero misión no inicializada o planta null");
            return;
        }

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarAnalisis(planta);
        }

        totalPlantasAnalizadas++;

        Debug.Log($"[MANAGER] 📊 Análisis recibido de Dron {idDron}: {planta.nombreComun} (Total: {totalPlantasAnalizadas})");

        if (uiController != null)
        {
            uiController.MostrarAnalisis(planta, idDron);
        }
        else
        {
            Debug.LogWarning($"[MANAGER] ⚠️ UIController no disponible para mostrar análisis");
        }

        // Registrar alertas específicas
        if (planta.EstaListaParaCosechar())
        {
            Debug.Log($"[MANAGER] 🌾 {planta.nombreComun} lista para cosechar");
            uiController?.RegistrarAlerta(planta, idDron, "🌾 Lista para cosechar");
        }

        if (planta.EstaMuyVerde())
        {
            Debug.Log($"[MANAGER] 🥬 {planta.nombreComun} muy verde");
            uiController?.RegistrarAlerta(planta, idDron, "🥬 Planta muy verde");
        }

        if (planta.TienePlagaActiva())
        {
            totalPlagasDetectadas++;
            Debug.Log($"[MANAGER] 🐛 Plaga activa en {planta.nombreComun} (Total: {totalPlagasDetectadas})");
            uiController?.RegistrarAlerta(planta, idDron, "🐛 Plaga detectada");
        }

        // NUEVA: Verificar necesidad de riego
        if (planta.NecesitaRiego())
        {
            Debug.Log($"[MANAGER] 💧 {planta.nombreComun} necesita riego urgente ({planta.humedad:F0}%)");
            uiController?.RegistrarAlerta(planta, idDron, "💧 Necesita riego urgente");
        }
    }

    public void NotificarAlerta(PlantaData planta, int idDron)
    {
        if (!misionInicializada || planta == null) 
        {
            Debug.LogWarning($"[MANAGER] ⚠️ NotificarAlerta llamado pero misión no inicializada o planta null");
            return;
        }

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarPlaga();
        }

        Debug.Log($"[MANAGER] 🚨 ALERTA de Dron {idDron}: Plaga en {planta.nombreComun}");

        if (uiController != null)
        {
            uiController.RegistrarAlerta(planta, idDron);
        }
        else
        {
            Debug.LogWarning($"[MANAGER] ⚠️ UIController no disponible para mostrar alerta");
        }
    }

    public void NotificarAccion(string accion, PlantaData planta, int idDron)
    {
        if (!misionInicializada || planta == null) 
        {
            Debug.LogWarning($"[MANAGER] ⚠️ NotificarAccion llamado pero misión no inicializada o planta null");
            return;
        }

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].RegistrarAccion(accion);
        }

        // Log detallado según el tipo de acción
        string emoji = "🔧";
        if (accion.Contains("pesticida") || accion.Contains("Pesticida"))
            emoji = "💉";
        else if (accion.Contains("osecha") || accion.Contains("Cosecha"))
            emoji = "🌾";
        else if (accion.Contains("verde") || accion.Contains("Verde"))
            emoji = "🥬";
        else if (accion.Contains("RIEGO") || accion.Contains("Riego"))
            emoji = "💧";

        Debug.Log($"[MANAGER] {emoji} Acción de Dron {idDron}: {accion} en {planta.nombreComun}");

        if (uiController != null)
        {
            uiController.RegistrarAccion(accion, planta, idDron);
        }
        else
        {
            Debug.LogWarning($"[MANAGER] ⚠️ UIController no disponible para registrar acción: {accion}");
        }
    }

    public void NotificarMisionCompleta(int idDron, int plantasAnalizadas, int plagasDetectadas, int cosechadas)
    {
        if (!misionInicializada) 
        {
            Debug.LogWarning($"[MANAGER] ⚠️ NotificarMisionCompleta llamado pero misión no inicializada");
            return;
        }

        if (reportesDrones.ContainsKey(idDron))
        {
            reportesDrones[idDron].MisionCompleta(plantasAnalizadas, plagasDetectadas, cosechadas);
        }

        totalCosechadas += cosechadas;

        Debug.Log($"[MANAGER] ✅ Dron {idDron} completó su misión:");
        Debug.Log($"  - Plantas analizadas: {plantasAnalizadas}");
        Debug.Log($"  - Plagas detectadas: {plagasDetectadas}");
        Debug.Log($"  - Plantas cosechadas: {cosechadas}");

        // Verificar si todos terminaron
        bool todosProcesados = reportesDrones.Values.All(r => r.misionCompleta);

        if (todosProcesados)
        {
            Debug.Log("[MANAGER] 🎯 Todos los drones completaron sus misiones");
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
        int necesitanRiego = todasLasPlantas.Count(p => p.NecesitaRiego());
        float saludProm = todasLasPlantas.Average(p => p.saludGeneral);
        float humedadProm = todasLasPlantas.Average(p => p.humedad);

        Debug.Log("\n════ ESTADÍSTICAS GLOBALES DEL CAMPO ════");
        Debug.Log($"Total plantas: {total}");
        Debug.Log($"Plantas con plaga: {conPlaga} ({(float)conPlaga / total * 100:F1}%)");
        Debug.Log($"Plantas maduras: {maduras} ({(float)maduras / total * 100:F1}%)");
        Debug.Log($"Plantas que necesitan riego: {necesitanRiego} ({(float)necesitanRiego / total * 100:F1}%)");
        Debug.Log($"Alertas IoT críticas: {alertas}");
        Debug.Log($"Salud promedio del campo: {saludProm:F1}%");
        Debug.Log($"Humedad promedio del campo: {humedadProm:F1}%");
        Debug.Log("═════════════════════════════════════════");
    }

    // ════════════════════════════════════════════════════════════
    // MÉTODOS PÚBLICOS PARA INTEGRACIÓN CON AGENTE DE RIEGO
    // ════════════════════════════════════════════════════════════

    /// <summary>
    /// Obtiene todas las plantas del campo (para el agente de riego)
    /// </summary>
    public List<PlantaData> ObtenerTodasLasPlantas()
    {
        return todasLasPlantas;
    }

    /// <summary>
    /// Obtiene plantas que necesitan atención inmediata
    /// </summary>
    public List<PlantaData> ObtenerPlantasCriticas()
    {
        return todasLasPlantas
            .Where(p => p != null && !p.cosechada && 
                   (p.NecesitaRiego() || p.TienePlagaActiva() || p.saludGeneral < 40f))
            .ToList();
    }

    /// <summary>
    /// Verifica si la misión está inicializada
    /// </summary>
    public bool MisionEstaInicializada()
    {
        return misionInicializada;
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