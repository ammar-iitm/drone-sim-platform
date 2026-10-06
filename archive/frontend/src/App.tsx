import { useState } from 'react';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('Live Dashboard');

  const screens = {
    'Live Dashboard': '/stitch/screen1.html',
    'Scenario Builder': '/stitch/screen2.html',
    'AAR Reports': '/stitch/screen3.html',
    'Unit Roster': '/stitch/screen4.html',
    'Readiness Matrix': '/stitch/screen5.html',
    'Flight Inspector': '/stitch/screen6.html'
  };

  return (
    <div className="w-screen h-screen bg-[#1E1E1E] text-white overflow-hidden flex flex-col">
      {/* Top Navigation Router for the Prototype */}
      <div className="bg-black/90 p-3 flex justify-center gap-6 border-b border-green-500/30 z-[100] shadow-lg shrink-0">
        {Object.entries(screens).map(([name, _]) => (
          <button 
            key={name}
            onClick={() => setCurrentScreen(name)}
            className={`font-mono text-sm px-3 py-1 rounded transition-colors ${
              currentScreen === name 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50 shadow-[0_0_10px_rgba(0,255,65,0.2)]' 
                : 'text-gray-400 hover:text-green-300 hover:bg-gray-800'
            }`}
          >
            {name}
          </button>
        ))}
      </div>
      
      {/* Fullscreen Iframe Rendering the exact Stitch HTML */}
      <div className="flex-1 w-full bg-black">
        <iframe 
          src={(screens as any)[currentScreen]} 
          className="w-full h-full border-none"
          title={currentScreen}
        />
      </div>
    </div>
  );
}
