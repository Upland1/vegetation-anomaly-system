using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target; 

    [Header("Ajustes de Cámara")]
    public Vector3 offset = new Vector3(0, 10, -8); 
    public float smoothSpeed = 5.0f; // Velocidad de seguimiento
    public float anguloFijo = 50.0f; // Ángulo fijo hacia abajo (Vista aérea)

    void LateUpdate()
    {
        if (target == null) return;

        // Calcular posición deseada
        Vector3 desiredPosition = target.position + offset;
        
        // Moverse suavemente 
        Vector3 smoothedPosition = Vector3.Lerp(transform.position, desiredPosition, smoothSpeed * Time.deltaTime);
        transform.position = smoothedPosition;

        // Rotación Fija
        transform.rotation = Quaternion.Euler(anguloFijo, 0, 0);
    }
}
