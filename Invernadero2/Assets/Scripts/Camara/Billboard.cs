using UnityEngine;

public class Billboard : MonoBehaviour
{
    void LateUpdate()
    {
        // Busca la cámara principal automáticamente
        Camera camara = Camera.main;

        if (camara != null)
        {
            // Paso A: Voltea a ver a la cámara
            transform.LookAt(transform.position + camara.transform.rotation * Vector3.forward,
                             camara.transform.rotation * Vector3.up);
        }
    }
}