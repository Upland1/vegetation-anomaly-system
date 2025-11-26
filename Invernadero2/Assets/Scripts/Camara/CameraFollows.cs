using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target; // Arrastra el Dron aquí

    [Header("Ajustes de Cámara")]
    public Vector3 offset = new Vector3(0, 10, -8); // Más alto para ver mejor el cultivo
    public float smoothSpeed = 5.0f; // Velocidad de seguimiento
    public float anguloFijo = 50.0f; // Ángulo fijo hacia abajo (Vista aérea)

    void LateUpdate()
    {
        if (target == null) return;

        // 1. Calcular posición deseada (Dron + Offset)
        Vector3 desiredPosition = target.position + offset;
        
        // 2. Moverse suavemente (Usando Time.deltaTime para que sea fluido)
        Vector3 smoothedPosition = Vector3.Lerp(transform.position, desiredPosition, smoothSpeed * Time.deltaTime);
        transform.position = smoothedPosition;

        // 3. Rotación Fija (Mejor que LookAt para que no se maree)
        transform.rotation = Quaternion.Euler(anguloFijo, 0, 0);
    }
}
