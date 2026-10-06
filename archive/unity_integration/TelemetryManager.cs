using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Net.WebSockets;
using UnityEngine;

// Serializable classes to match our Backend JSON structure
[Serializable]
public class DroneData {
    public string id;
    public string type;
    public float[] position;
    public string status;
}

[Serializable]
public class SimulationPayload {
    public float timeElapsed;
    public List<DroneData> drones;
}

[Serializable]
public class SimulationMessage {
    public string type;
    public string payload; // Stored as string to allow sending complex JSON objects via JsonUtility
}

[Serializable]
public class EventPayload {
    public string level;
    public string message;
    public string time;
}

public class TelemetryManager : MonoBehaviour
{
    [Header("Backend Connection")]
    public string serverUrl = "ws://localhost:3001";
    
    private ClientWebSocket websocket;
    private float timeElapsed = 0f;
    private bool isConnected = false;

    async void Start()
    {
        websocket = new ClientWebSocket();
        try
        {
            Uri serverUri = new Uri(serverUrl);
            await websocket.ConnectAsync(serverUri, CancellationToken.None);
            isConnected = true;
            Debug.Log("Connected to AAR Backend Dashboard!");
            
            // Start listening for Instructor Commands
            ReceiveMessages();
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to connect to backend: {e.Message}");
        }
    }

    void Update()
    {
        if (!isConnected) return;
        
        timeElapsed += Time.deltaTime;

        // In a real game, you would push updates every 0.1s to 0.5s instead of every frame
        // to prevent flooding the network. For this example, we'll assume a separate coroutine
        // or invoke repeating calls SendSimulationUpdate().
    }

    /// <summary>
    /// Call this method 5-10 times a second to update the dashboard with live positions.
    /// </summary>
    public async void SendSimulationUpdate(List<DroneData> activeDrones)
    {
        if (!isConnected || websocket.State != WebSocketState.Open) return;

        SimulationPayload payload = new SimulationPayload {
            timeElapsed = this.timeElapsed,
            drones = activeDrones
        };

        // Create main wrapper
        string jsonPayload = JsonUtility.ToJson(payload);
        
        // Manual JSON construction since Unity's built-in JsonUtility can't easily nest stringified objects natively without wrappers.
        string fullMessage = $"{{\"type\":\"SIMULATION_UPDATE\",\"payload\":{jsonPayload}}}";
        
        await SendWebSocketMessage(fullMessage);
    }

    /// <summary>
    /// Call this whenever a trainee does something notable (shoots, spots a drone, gets jammed).
    /// </summary>
    public async void LogEvent(string level, string messageText)
    {
        if (!isConnected || websocket.State != WebSocketState.Open) return;

        EventPayload ev = new EventPayload {
            level = level,
            message = messageText,
            time = $"T+{(int)timeElapsed}s"
        };
        
        string jsonPayload = JsonUtility.ToJson(ev);
        string fullMessage = $"{{\"type\":\"NEW_EVENT\",\"payload\":{jsonPayload}}}";
        
        await SendWebSocketMessage(fullMessage);
        Debug.Log($"Event Logged to AAR: {messageText}");
    }

    private async Task SendWebSocketMessage(string message)
    {
        byte[] buffer = Encoding.UTF8.GetBytes(message);
        var segment = new ArraySegment<byte>(buffer);
        await websocket.SendAsync(segment, WebSocketMessageType.Text, true, CancellationToken.None);
    }

    private async void ReceiveMessages()
    {
        byte[] buffer = new byte[1024];
        
        while (websocket.State == WebSocketState.Open)
        {
            try
            {
                var result = await websocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await websocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                }
                else
                {
                    string receivedMessage = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    ProcessInstructorCommand(receivedMessage);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"WebSocket Receive Error: {ex.Message}");
                break;
            }
        }
    }

    private void ProcessInstructorCommand(string jsonMessage)
    {
        // Example: {"type":"INSTRUCTOR_COMMAND","payload":"SPAWN_KAMIKAZE"}
        if (jsonMessage.Contains("INSTRUCTOR_COMMAND"))
        {
            if (jsonMessage.Contains("SPAWN_KAMIKAZE"))
            {
                Debug.Log("COMMAND RECEIVED: Spawning Kamikaze Drone!");
                // Trigger your Unity Spawner script here...
                
                LogEvent("CRITICAL", "Instructor spawned Kamikaze drone.");
            }
            else if (jsonMessage.Contains("TOGGLE_JAMMING"))
            {
                Debug.Log("COMMAND RECEIVED: Toggling Jamming effect!");
                // Trigger your post-processing/UI glitch effect here...
                
                LogEvent("INFO", "Instructor toggled Radar Jamming.");
            }
        }
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null && websocket.State == WebSocketState.Open)
        {
            await websocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Game Closed", CancellationToken.None);
        }
    }
}
