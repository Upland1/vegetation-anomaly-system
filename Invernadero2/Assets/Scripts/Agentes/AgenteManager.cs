using UnityEngine;
using TMPro; // Necesario para los textos de la UI

public class AgenteManager : MonoBehaviour
{
    // Singleton: Permite que el Dron encuentre al Manager fácilmente
    public static AgenteManager Instance;

    [Header("Referencias UI")]
    public TextMeshProUGUI textoEstado;   // Arrastra aquí el texto que dice "Analizando..."
    public TextMeshProUGUI textoAlertas;  // Arrastra aquí el texto que dice "ALERTA"

    // Contadores internos
    private int contadorAlertas = 0;

    void Awake()
    {
        // Configuración básica del Singleton
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    // Función llamada por el Dron para actualizar el estado en pantalla
    public void MostrarAnalisisUI(PlantaData planta)
    {
        if (textoEstado != null)
        {
            string estadoSalud = planta.tienePlaga ? "<color=red>INFECTADA</color>" : "<color=green>SANA</color>";
            textoEstado.text = $"DRON ESTADO:\nObjetivo: {planta.name}\nMadurez: {planta.nivelMaduracion}/10\nDiagnóstico: {estadoSalud}";
        }
    }

    // Función llamada por el Dron cuando detecta una plaga
    public void RegistrarAlerta(string nombrePlanta)
    {
        contadorAlertas++;
        if (textoAlertas != null)
        {
            textoAlertas.text = $"¡ALERTA CRÍTICA!\nZona Afectada: {nombrePlanta}\nTotal Detectadas: {contadorAlertas}";
            textoAlertas.color = Color.red; // Pone el texto en rojo intenso
        }
        Debug.LogWarning($"[MANAGER] Se ha registrado una nueva plaga en {nombrePlanta}");
    }
}