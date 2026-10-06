const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

// In-memory state (for prototype)
let sessionState = {
  activeSession: true,
  traineeName: 'John Doe (Unit A)',
  timeElapsed: 0,
  baseHealth: 100,
  events: [],
  metrics: {
    detectionTime: 0,
    classificationAccuracy: 100,
    engagementScore: 'Pending',
  },
  drones: [] // [{ id, type, position: [x,y,z], status }]
};

// Basic REST API
app.get('/api/status', (req, res) => {
  res.json({ status: 'running', sessionState });
});

// WebSocket Server for live telemetry
wss.on('connection', (ws) => {
  console.log('Client connected to WebSocket.');

  // Send initial state upon connection
  ws.send(JSON.stringify({ type: 'INIT_STATE', payload: sessionState }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      switch (data.type) {
        case 'SIMULATION_UPDATE':
          // Update drone positions and trainee status
          sessionState.drones = data.payload.drones;
          sessionState.timeElapsed = data.payload.timeElapsed;
          
          // Broadcast to all connected clients (e.g., dashboard)
          wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'SIMULATION_UPDATE', payload: sessionState }));
            }
          });
          break;
        
        case 'NEW_EVENT':
          // A new event occurred (e.g., target destroyed, jammer activated)
          sessionState.events.unshift(data.payload); // Add to beginning
          // Keep only last 50 events
          if (sessionState.events.length > 50) sessionState.events.pop();
          
          wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'NEW_EVENT', payload: data.payload }));
            }
          });
          break;

        case 'INSTRUCTOR_COMMAND':
          // E.g., spawn drone, change weather
          console.log('Instructor commanded:', data.payload);
          // Broadcast command to simulation client
          wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'INSTRUCTOR_COMMAND', payload: data.payload }));
            }
          });
          break;
      }
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected.');
  });
});

server.listen(PORT, () => {
  console.log(`Backend Server running on port ${PORT}`);
  console.log(`WebSocket server listening on ws://localhost:${PORT}`);
});
