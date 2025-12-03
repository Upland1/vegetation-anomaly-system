using UnityEngine;
using System.Collections.Generic;

public class CameraFollow : MonoBehaviour
{
    [Header("Referencias")]
    public List<Transform> targets = new List<Transform>();
    public bool autoFindDrones = true;

    [Header("Ajustes Base de Cámara")]
    public float heightAboveTargets = 30f;
    public float distanceBehind = 60f;
    public float smoothSpeed = 5f;

    [Header("Límites de Distancia y Altura")]
    public float minFollowDistance = 20f;
    public float maxFollowDistance = 200f;
    public float minFollowHeight = 10f;
    public float maxFollowHeight = 80f;

    [Header("Zoom Automático")]
    public bool enableDynamicZoom = true;
    public float spreadZoomMultiplier = 0.4f;
    public float extraPadding = 4f;

    [Header("Zoom Manual (Scroll)")]
    public float zoomStepDistance = 5f;
    public float zoomStepHeight = 2f;

    [Header("Rotación Manual 360°")]
    public float rotationSpeed = 120f;
    private float currentYaw = 0f;
    private float currentPitch = 45f;
    public float minPitch = 10f;
    public float maxPitch = 80f;

    private Vector3 velocity = Vector3.zero;

    void Start()
    {
        if (autoFindDrones)
            FindAllDrones();
    }

    void LateUpdate()
    {
        if (targets.Count == 0) return;

        targets.RemoveAll(t => t == null);
        if (targets.Count == 0) return;

        // ---------------------------------------
        //  ZOOM MANUAL (SCROLL DEL MOUSE)
        // ---------------------------------------
        float scroll = Input.GetAxis("Mouse ScrollWheel");

        if (scroll > 0f)
        {
            distanceBehind -= zoomStepDistance;
            heightAboveTargets -= zoomStepHeight;
        }
        else if (scroll < 0f)
        {
            distanceBehind += zoomStepDistance;
            heightAboveTargets += zoomStepHeight;
        }

        distanceBehind = Mathf.Clamp(distanceBehind, minFollowDistance, maxFollowDistance);
        heightAboveTargets = Mathf.Clamp(heightAboveTargets, minFollowHeight, maxFollowHeight);

        // ---------------------------------------
        //        ROTACIÓN MANUAL 360°
        // ---------------------------------------
        if (Input.GetMouseButton(1)) // clic derecho
        {
            float mouseX = Input.GetAxis("Mouse X");
            float mouseY = Input.GetAxis("Mouse Y");

            currentYaw += mouseX * rotationSpeed * Time.deltaTime;
            currentPitch -= mouseY * rotationSpeed * Time.deltaTime;

            currentPitch = Mathf.Clamp(currentPitch, minPitch, maxPitch);
        }

        // ---------------------------------------
        //            CENTRO DEL GRUPO
        // ---------------------------------------
        Vector3 centerPoint = GetCenterPoint();

        // ---------------------------------------
        //         ZOOM AUTOMÁTICO
        // ---------------------------------------
        float dynamicDistance = distanceBehind;
        float dynamicHeight = heightAboveTargets;

        if (enableDynamicZoom && targets.Count > 1)
        {
            float spread = GetGroupSpread() + extraPadding;

            dynamicDistance = Mathf.Clamp(
                distanceBehind + spread * spreadZoomMultiplier,
                minFollowDistance,
                maxFollowDistance
            );

            dynamicHeight = Mathf.Clamp(
                heightAboveTargets + spread * (spreadZoomMultiplier * 0.5f),
                minFollowHeight,
                maxFollowHeight
            );
        }

        // ---------------------------------------
        //       POSICIÓN ORBITAL REAL
        // ---------------------------------------
        Quaternion rot = Quaternion.Euler(currentPitch, currentYaw, 0);

        Vector3 offset = rot * new Vector3(0, 0, -dynamicDistance);
        offset.y += dynamicHeight;

        Vector3 desiredPosition = centerPoint + offset;

        transform.position = Vector3.SmoothDamp(
            transform.position,
            desiredPosition,
            ref velocity,
            1f / smoothSpeed
        );

        // ---------------------------------------
        //         MIRAR AL CENTRO SIEMPRE
        // ---------------------------------------
        Quaternion lookRotation = Quaternion.LookRotation(centerPoint - transform.position);
        transform.rotation = Quaternion.Slerp(transform.rotation, lookRotation, Time.deltaTime * smoothSpeed);
    }

    // ==============================
    //     FUNCIONES AUXILIARES
    // ==============================

    Vector3 GetCenterPoint()
    {
        if (targets.Count == 1)
            return targets[0].position;

        Bounds b = new Bounds(targets[0].position, Vector3.zero);
        foreach (Transform t in targets)
            b.Encapsulate(t.position);

        return b.center;
    }

    float GetGroupSpread()
    {
        if (targets.Count <= 1)
            return 0f;

        Bounds b = new Bounds(targets[0].position, Vector3.zero);
        foreach (Transform t in targets)
            b.Encapsulate(t.position);

        return Mathf.Max(b.size.x, b.size.z);
    }

    // ==============================
    //     CONTROL DE DRONES
    // ==============================

    public void FindAllDrones()
    {
        targets.Clear();

        AgenteFisico[] agentes = FindObjectsByType<AgenteFisico>(FindObjectsSortMode.None);
        foreach (var agente in agentes)
            targets.Add(agente.transform);

        Debug.Log($"CameraFollow: Se encontraron {targets.Count} drones.");
    }

    public void AddTarget(Transform t)
    {
        if (t != null && !targets.Contains(t))
            targets.Add(t);
    }

    public void RemoveTarget(Transform t)
    {
        if (targets.Contains(t))
            targets.Remove(t);
    }
}
