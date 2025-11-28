using UnityEngine;
using System.Collections.Generic;

public class CameraFollow : MonoBehaviour
{
    [Header("Referencias")]
    public List<Transform> targets = new List<Transform>(); // Lista de drones a seguir
    public bool autoFindDrones = true; // Buscar drones automáticamente al inicio
    
    [Header("Ajustes de Cámara")]
    public float heightAboveTargets = 60f; // Altura sobre los drones (Y) - Reducido a 3/4
    public float distanceBehind = 45f; // Distancia hacia atrás (Z) - Reducido a 3/4
    public float smoothSpeed = 5.0f; // Velocidad de seguimiento
    public float cameraAngle = 45.0f; // Ángulo de inclinación de la cámara
    
    [Header("Zoom Dinámico")]
    public bool enableDynamicZoom = true; // Activar zoom automático basado en dispersión
    public float minDistanceMultiplier = 1.5f; // Multiplicador mínimo de distancia
    public float maxDistanceMultiplier = 3.5f; // Multiplicador máximo de distancia
    public float minHeight = 30f; // Altura mínima - Reducido a 3/4
    public float maxHeight = 112.5f; // Altura máxima - Reducido a 3/4 (150 * 0.75 = 112.5)
    public float extraPadding = 15f; // Padding extra - Reducido a 3/4
    
    private Vector3 velocity = Vector3.zero;

    void Start()
    {
        if (autoFindDrones)
        {
            FindAllDrones();
        }
    }

    void LateUpdate()
    {
        if (targets == null || targets.Count == 0) return;

        // Eliminar targets nulos (drones destruidos)
        targets.RemoveAll(t => t == null);
        
        if (targets.Count == 0) return;

        // Calcular el centro de todos los drones
        Vector3 centerPoint = GetCenterPoint();
        
        // Calcular la dispersión del grupo
        float groupSpread = GetGroupSpread();
        
        // Calcular distancia y altura dinámicas basadas en la dispersión
        float dynamicHeight = heightAboveTargets;
        float dynamicDistance = distanceBehind;
        
        if (enableDynamicZoom && targets.Count > 1)
        {
            // Cuanto más dispersos estén los drones, más lejos debe estar la cámara
            float spreadFactor = groupSpread + extraPadding;
            
            dynamicHeight = Mathf.Clamp(
                heightAboveTargets + (spreadFactor * minDistanceMultiplier), 
                minHeight, 
                maxHeight
            );
            
            dynamicDistance = Mathf.Clamp(
                distanceBehind + (spreadFactor * minDistanceMultiplier * 0.8f),
                distanceBehind,
                distanceBehind * maxDistanceMultiplier
            );
        }
        
        // Calcular posición deseada: centro + offset vertical y hacia atrás
        Vector3 desiredPosition = centerPoint + new Vector3(0, dynamicHeight, -dynamicDistance);
        
        // Moverse suavemente
        transform.position = Vector3.SmoothDamp(
            transform.position, 
            desiredPosition, 
            ref velocity, 
            1f / smoothSpeed
        );
        
        // Mirar hacia el punto central con el ángulo especificado
        Vector3 lookDirection = centerPoint - transform.position;
        if (lookDirection != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(lookDirection);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, smoothSpeed * Time.deltaTime);
        }
    }

    // Encuentra el punto central entre todos los drones
    Vector3 GetCenterPoint()
    {
        if (targets.Count == 1)
        {
            return targets[0].position;
        }

        Bounds bounds = new Bounds(targets[0].position, Vector3.zero);
        foreach (Transform target in targets)
        {
            if (target != null)
            {
                bounds.Encapsulate(target.position);
            }
        }

        return bounds.center;
    }

    // Calcula qué tan dispersos están los drones
    float GetGroupSpread()
    {
        if (targets.Count == 1)
        {
            return 0f;
        }

        Bounds bounds = new Bounds(targets[0].position, Vector3.zero);
        foreach (Transform target in targets)
        {
            if (target != null)
            {
                bounds.Encapsulate(target.position);
            }
        }

        // Retorna la mayor dimensión horizontal (X o Z)
        return Mathf.Max(bounds.size.x, bounds.size.z);
    }

    // Busca automáticamente todos los GameObjects con el script AgenteFisico
    public void FindAllDrones()
    {
        targets.Clear();
        
        // Buscar todos los objetos con el componente AgenteFisico
        AgenteFisico[] agentes = FindObjectsOfType<AgenteFisico>();
        
        foreach (AgenteFisico agente in agentes)
        {
            targets.Add(agente.transform);
        }
        
        Debug.Log($"CameraFollow: Se encontraron {targets.Count} drones con AgenteFisico");
    }

    // Añadir un drone manualmente
    public void AddTarget(Transform newTarget)
    {
        if (newTarget != null && !targets.Contains(newTarget))
        {
            targets.Add(newTarget);
        }
    }

    // Remover un drone manualmente
    public void RemoveTarget(Transform targetToRemove)
    {
        if (targets.Contains(targetToRemove))
        {
            targets.Remove(targetToRemove);
        }
    }

    // Visualización en el editor (Gizmos)
    void OnDrawGizmos()
    {
        if (targets == null || targets.Count == 0) return;

        // Dibujar líneas hacia cada drone
        Gizmos.color = Color.cyan;
        Vector3 center = GetCenterPoint();
        
        foreach (Transform target in targets)
        {
            if (target != null)
            {
                Gizmos.DrawLine(center, target.position);
                Gizmos.DrawWireSphere(target.position, 2f);
            }
        }

        // Dibujar el centro
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(center, 3f);
        
        // Dibujar la posición deseada de la cámara
        Gizmos.color = Color.green;
        float spread = GetGroupSpread();
        float dynHeight = heightAboveTargets;
        float dynDist = distanceBehind;
        
        if (enableDynamicZoom && targets.Count > 1)
        {
            float spreadFactor = spread + extraPadding;
            dynHeight = Mathf.Clamp(
                heightAboveTargets + (spreadFactor * minDistanceMultiplier), 
                minHeight, 
                maxHeight
            );
            dynDist = Mathf.Clamp(
                distanceBehind + (spreadFactor * minDistanceMultiplier * 0.8f),
                distanceBehind,
                distanceBehind * maxDistanceMultiplier
            );
        }
        
        Vector3 camPos = center + new Vector3(0, dynHeight, -dynDist);
        Gizmos.DrawWireSphere(camPos, 5f);
        Gizmos.DrawLine(camPos, center);
    }
}