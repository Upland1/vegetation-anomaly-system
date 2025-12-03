using UnityEngine;

public class AudioListenerManager : MonoBehaviour
{
    void Awake()
    {
        AudioListener[] listeners = FindObjectsByType<AudioListener>(FindObjectsSortMode.None);
        
        if (listeners.Length > 1)
        {
            // Mantener solo el de la cámara principal
            Camera mainCam = Camera.main;
            AudioListener mainListener = mainCam != null ? mainCam.GetComponent<AudioListener>() : null;
            
            for (int i = 0; i < listeners.Length; i++)
            {
                if (listeners[i] != mainListener)
                {
                    listeners[i].enabled = false;
                }
            }
            
            Debug.Log($"[Audio] {listeners.Length - 1} AudioListeners duplicados desactivados.");
        }
    }
}