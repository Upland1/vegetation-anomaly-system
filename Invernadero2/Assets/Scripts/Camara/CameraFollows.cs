using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target;       // El Dron a seguir
    public Vector3 offset = new Vector3(0, 5, -8); // Posición relativa (Arriba y atrás)
    public float smoothSpeed = 0.125f; // Suavizado del movimiento

    void LateUpdate()
    {
        if (target == null) return;

        // Calcular posición deseada
        Vector3 desiredPosition = target.position + offset;
        
        // Moverse suavemente hacia esa posición
        Vector3 smoothedPosition = Vector3.Lerp(transform.position, desiredPosition, smoothSpeed);
        transform.position = smoothedPosition;

        // Mirar siempre al dron
        transform.LookAt(target);
    }
}
