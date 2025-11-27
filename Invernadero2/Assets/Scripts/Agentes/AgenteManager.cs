using UnityEngine;
using TMPro; 

public class AgenteManager : MonoBehaviour
{
    public static AgenteManager Instance;

    [Header("Referencias UI")]
    public TextMeshProUGUI textoEstado;   
    public TextMeshProUGUI textoAlertas;  
    
    private int alertasCount = 0;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    public void MostrarAnalisisUI(PlantaData planta)
    {
        if(textoEstado != null)
        {
            string estado = planta.tienePlaga ? "INFECTADA" : "SANA";
            
            // Usamos 'nombreComun' para coincidir con PlantaData
            textoEstado.text = $"MONITOREO EN VIVO\n" +
                               $"Target: {planta.nombreComun}\n" + 
                               $"Madurez: {planta.nivelMaduracion:F1}/10\n" +
                               $"Salud: {estado}";
        }
    }

    public void RegistrarAlerta(string nombrePlanta)
    {
        alertasCount++;
        if(textoAlertas != null)
        {
            textoAlertas.text = $"¡ALERTA DE PLAGA!\n" +
                                $"Ubicación: {nombrePlanta}\n" +
                                $"Contador Plagas: {alertasCount}";
            textoAlertas.color = Color.red; 
        }
    }
}