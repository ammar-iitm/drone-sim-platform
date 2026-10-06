const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
  console.log('Dummy Simulation connected to backend.');
  
  let timeElapsed = 0;
  
  // Simulate regular telemetry updates (5Hz)
  setInterval(() => {
    timeElapsed += 0.2;
    ws.send(JSON.stringify({
      type: 'SIMULATION_UPDATE',
      payload: {
        timeElapsed: timeElapsed,
        drones: []
      }
    }));
  }, 200);

  // Simulate random events
  setInterval(() => {
    const events = [
      { level: 'INFO', message: 'Trainee scanning sector 4...', time: `T+${Math.floor(timeElapsed)}s` },
      { level: 'CRITICAL', message: 'Radar anomaly detected at bearing 045.', time: `T+${Math.floor(timeElapsed)}s` },
      { level: 'INFO', message: 'Trainee locked on target.', time: `T+${Math.floor(timeElapsed)}s` },
    ];
    const randomEvent = events[Math.floor(Math.random() * events.length)];
    ws.send(JSON.stringify({
      type: 'NEW_EVENT',
      payload: randomEvent
    }));
  }, 3500);
});

ws.on('message', (message) => {
  const data = JSON.parse(message);
  if (data.type === 'INSTRUCTOR_COMMAND') {
    console.log('\n--- COMMAND RECEIVED FROM DASHBOARD ---');
    console.log(data.payload);
    
    // Echo back an event that the command was executed
    ws.send(JSON.stringify({
      type: 'NEW_EVENT',
      payload: { level: 'CRITICAL', message: `SYSTEM: Executed command [${data.payload}]`, time: 'LIVE' }
    }));
  }
});
