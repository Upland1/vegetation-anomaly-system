using UnityEngine;

public class Billboard : MonoBehaviour
{
    [Header("Configuración")]
    public bool lockY = false; // Bloquear rotación en eje Y (para mantener UI horizontal)
    
    private Camera mainCamera;

    void Start()
    {
        // Cachear la referencia a la cámara principal
        mainCamera = Camera.main;
        
        if (mainCamera == null)
        {
            Debug.LogWarning("Billboard: No se encontró una cámara principal en la escena.");
        }
    }

    void LateUpdate()
    {
        // Si no hay cámara cacheada, intentar buscarla nuevamente
        if (mainCamera == null)
        {
            mainCamera = Camera.main;
            if (mainCamera == null) return;
        }

        // Calcular la dirección hacia la cámara
        Vector3 directionToCamera = mainCamera.transform.position - transform.position;
        
        // Si queremos bloquear el eje Y (para mantener UI horizontal)
        if (lockY)
        {
            directionToCamera.y = 0;
        }
        
        // Verificar que la dirección no sea cero
        if (directionToCamera.sqrMagnitude > 0.001f)
        {
            // Rotar para mirar hacia la cámara
            Quaternion targetRotation = Quaternion.LookRotation(directionToCamera);
            transform.rotation = targetRotation;
        }
    }

    // Método alternativo (más simple) para billboard
    void AlternativeBillboard()
    {
        if (mainCamera != null)
        {
            // Voltea a ver a la cámara usando la orientación de la cámara
            transform.LookAt(transform.position + mainCamera.transform.rotation * Vector3.forward,
                            mainCamera.transform.rotation * Vector3.up);
        }
    }
}