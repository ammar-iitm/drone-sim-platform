import React from 'react';

export default function ScenarioBuilder() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs" data-active-classes="bg-surface-container text-primary-container font-bold border-l-2 border-primary-container"><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="live-dashboard" href="#"><span className="material-symbols-outlined text-[18px]">grid_view</span><span>Live Dashboard</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span className="material-symbols-outlined text-[18px]">alt_route</span><span>Scenario Builder</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="aar-reports" href="#"><span className="material-symbols-outlined text-[18px]">summarize</span><span>AAR Reports</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="unit-roster" href="#"><span className="material-symbols-outlined text-[18px]">shield_person</span><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
{/*  Tactical Sidebar Active Route Synchronizer  */}

{/*  Top Scenario Command & Validation Bar  */}
<div className="w-full bg-surface-container-low px-space-lg py-space-md flex flex-col xl:flex-row xl:items-center justify-between gap-space-md shadow-sm">
<div className="flex flex-col gap-space-xs min-w-0">
<div className="flex flex-wrap items-center gap-space-sm">
<span className="px-space-sm py-space-xs bg-surface-container-highest text-primary-container font-label-sm text-label-sm font-bold uppercase tracking-wider">SEC-C2 // SCRIPTING ENGINE</span>
<span className="px-space-sm py-space-xs bg-error-container text-on-error-container font-label-sm text-label-sm font-bold uppercase tracking-widest animate-pulse">EXERCISE CLASSIFIED // LEVEL-4</span>
<div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span>REV: 04.9B</span>
<span>•</span>
<span>AUTHOR: TAC-COORD [SIM-DIR-08]</span>
</div>
</div>
<div className="flex flex-wrap items-baseline gap-space-md">
<h1 className="font-headline-md text-headline-md text-primary tracking-tight font-bold uppercase">OP-VIPER STRIKE // HYBRID MULTI-WAVE SWARM</h1>
<div className="flex items-center gap-space-sm">
<span className="px-space-sm py-space-xs bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm uppercase">STATE: <strong className="text-tertiary-fixed-dim">DRAFT / IN-EDIT</strong></span>
<span className="px-space-sm py-space-xs bg-surface-container-high text-on-surface font-label-sm text-label-sm uppercase">DUR: <strong className="font-telemetry-data text-telemetry-data text-secondary-container">18M 00S</strong></span>
<span className="px-space-sm py-space-xs bg-surface-container-high text-on-surface font-label-sm text-label-sm uppercase">DENSITY: <strong className="font-telemetry-data text-telemetry-data text-error">38 TARGETS</strong></span>
<span className="px-space-sm py-space-xs bg-surface-container-high text-on-surface font-label-sm text-label-sm uppercase">STRESS: <strong className="text-primary-container font-bold">LVL-4 ELITE</strong></span>
</div>
</div>
</div>
{/*  Action Pipeline Toolbar  */}
<div className="flex flex-wrap items-center gap-space-sm self-start xl:self-auto">
<button className="flex items-center gap-space-xs px-space-md py-space-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-colors" title="Check node graph logic and bounds" type="button">
<span className="material-symbols-outlined text-[16px] text-primary-container">rule</span>
<span>VALIDATE SIM</span>
</button>
<button className="flex items-center gap-space-xs px-space-md py-space-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-colors" type="button">
<span className="material-symbols-outlined text-[16px] text-secondary-container">fast_forward</span>
<span>DRY RUN (2X)</span>
</button>
<button className="flex items-center gap-space-xs px-space-md py-space-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">terminal</span>
<span>EXPORT YAML</span>
</button>
<button className="flex items-center gap-space-xs px-space-md py-space-sm bg-surface-container-highest hover:bg-surface-bright text-primary font-label-md text-label-md transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">save</span>
<span>COMPILE</span>
</button>
<button className="flex items-center gap-space-xs px-space-lg py-space-sm bg-primary-container hover:bg-primary-fixed-dim text-on-primary-container font-label-md text-label-md font-bold transition-all shadow-md" type="button">
<span className="material-symbols-outlined text-[18px]">rocket_launch</span>
<span>DEPLOY TO LIVE SIM</span>
</button>
</div>
</div>
{/*  Primary 3-Column Tactical Workspace  */}
<div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter p-space-md w-full bg-surface-dim">
{/*  ==========================================  */}
{/*  COLUMN 1: Wave Sequence & Timeline List     */}
{/*  ==========================================  */}
<div className="lg:col-span-3 flex flex-col gap-space-sm">
{/*  Sequence Master Header  */}
<div className="p-space-sm bg-surface-container-low flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-primary-container">format_list_numbered</span>
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface font-bold">WAVE INJECTION STACK</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm">4 PHASES REGISTERED</span>
</div>
{/*  Wave Cards List  */}
<div className="flex flex-col gap-space-sm">
{/*  Wave 01 (Compiled)  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-xs hover:bg-surface-container transition-all cursor-pointer">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="w-1.5 h-1.5 bg-primary-container"></span>
<span className="font-label-sm text-label-sm text-primary-container font-bold">PHASE 01 // T+00:00 - T+03:30</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-primary-fixed text-label-sm font-label-sm">COMPILED</span>
</div>
<div className="font-headline-sm text-headline-sm text-on-surface font-semibold">RECON INFILTRATION &amp; RADAR BAIT</div>
<div className="text-on-surface-variant font-body-sm text-body-sm line-clamp-2">4x Fixed-Wing EW loiter units. Altitude 4,500m MSL. Ingress bearing 340° deploying broadband RF chaff strobes.</div>
<div className="flex items-center justify-between pt-space-xs mt-space-xs bg-surface-container-lowest p-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span>UNITS: <strong className="text-on-surface">4 UCAV</strong></span>
<span>FREQ: <strong className="text-on-surface">S-BAND 2.4G</strong></span>
<span className="text-primary-container">RDY-PASS</span>
</div>
</div>
{/*  Wave 02 (Selected & Active in Editor)  */}
<div className="bg-surface-container p-space-md flex flex-col gap-space-xs shadow-md ring-1 ring-primary-container/40 relative">
<div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-container"></div>
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-primary-container animate-pulse"></span>
<span className="font-label-sm text-label-sm text-primary-container font-bold">PHASE 02 // T+03:30 - T+08:00</span>
</div>
<span className="px-space-xs py-0.5 bg-primary-container text-on-primary-container font-label-sm text-label-sm font-bold">ACTIVE EDITING</span>
</div>
<div className="font-headline-sm text-headline-sm text-primary font-bold">DIVERSIONARY FPV SATURATION</div>
<div className="text-on-surface-variant font-body-sm text-body-sm">12x FPV Kamikaze shaped-charge swarms executing twin pincer ingress along Bearing 045° and 120° at 150m AGL.</div>
{/*  Wave Micro Telemetry  */}
<div className="grid grid-cols-3 gap-space-xs mt-space-xs bg-surface-container-lowest p-space-xs">
<div className="flex flex-col">
<span className="text-on-surface-variant font-label-sm text-label-sm">CELL COUNT</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container">12 DRONES</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant font-label-sm text-label-sm">INGRESS VEL</span>
<span className="font-telemetry-data text-telemetry-data text-secondary-container">120 KTS</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant font-label-sm text-label-sm">THREAT TIER</span>
<span className="font-telemetry-data text-telemetry-data text-error">KINETIC HIGH</span>
</div>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm pt-space-xs">
<span className="flex items-center gap-space-xs"><span className="material-symbols-outlined text-[14px] text-tertiary-fixed-dim">sensors</span>EW JAM CONE: 030°-070°</span>
<span className="text-primary-container font-bold">SELECTED</span>
</div>
</div>
{/*  Wave 03 (Draft)  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-xs hover:bg-surface-container transition-all cursor-pointer opacity-85">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="w-1.5 h-1.5 bg-tertiary-fixed-dim"></span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-bold">PHASE 03 // T+08:00 - T+14:00</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-tertiary-fixed-dim font-label-sm text-label-sm">DRAFTING</span>
</div>
<div className="font-headline-sm text-headline-sm text-on-surface font-semibold">SWARM PINCH ATTACK &amp; EW JAMMING</div>
<div className="text-on-surface-variant font-body-sm text-body-sm line-clamp-2">18x Micro-Quadcopters coordinated swarm, synchronized strobe jamming with directional frequency sweep.</div>
<div className="flex items-center justify-between pt-space-xs mt-space-xs bg-surface-container-lowest p-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span>UNITS: <strong className="text-on-surface">18 QUADS</strong></span>
<span>BEARING: <strong className="text-on-surface">220° - 290°</strong></span>
<span className="text-tertiary-fixed-dim">INCOMPLETE</span>
</div>
</div>
{/*  Wave 04 (Queued)  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-xs hover:bg-surface-container transition-all cursor-pointer opacity-70">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="w-1.5 h-1.5 bg-outline"></span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-bold">PHASE 04 // T+14:00 - T+18:00</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm">QUEUED</span>
</div>
<div className="font-headline-sm text-headline-sm text-on-surface font-semibold">HEAVY KINETIC DRONE PENETRATOR</div>
<div className="text-on-surface-variant font-body-sm text-body-sm line-clamp-2">4x Shahed-type delta autonomous cruise loiterers carrying anti-radiation home-on-jam warheads.</div>
<div className="flex items-center justify-between pt-space-xs mt-space-xs bg-surface-container-lowest p-space-xs text-on-surface-variant font-label-sm text-label-sm">
<span>UNITS: <strong className="text-on-surface">4 HEAVY</strong></span>
<span>ALT: <strong className="text-on-surface">300m AGL</strong></span>
<span className="text-on-surface-variant">LOCKED</span>
</div>
</div>
</div>
{/*  Add New Wave Action Button  */}
<button className="w-full flex items-center justify-center gap-space-xs py-space-sm bg-surface-container hover:bg-surface-container-high text-primary-container font-label-md text-label-md uppercase tracking-wider transition-colors" type="button">
<span className="material-symbols-outlined text-[18px]">add_circle</span>
<span>+ ADD WAVE / INJECTION PHASE</span>
</button>
{/*  Global Trigger & Failure Conditions Card  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-sm mt-space-xs">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs text-on-surface font-label-sm text-label-sm font-bold uppercase">
<span className="material-symbols-outlined text-[16px] text-error">crisis_alert</span>
<span>AUTONOMOUS TRIGGER LOGIC</span>
</div>
<span className="font-label-sm text-label-sm text-primary-container">CASCADE ON</span>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col gap-space-xs">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">BRANCH TRIGGER A:</span>
<p className="font-label-md text-label-md text-on-surface">IF Trainee ADA Ammo &lt; 35% OR Defense Battery Breach &gt; 1 THEN Fast-Forward Wave 04 (+180s earlier).</p>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col gap-space-xs">
<span className="text-on-surface-variant font-label-sm text-label-sm uppercase">SIM TERMINATION CRITERIA:</span>
<div className="flex items-center justify-between text-on-surface font-body-sm text-body-sm">
<span>• Base Radar Mast Kill:</span>
<span className="text-error font-telemetry-data text-telemetry-data font-bold">MISSION FAIL</span>
</div>
<div className="flex items-center justify-between text-on-surface font-body-sm text-body-sm">
<span>• ≥90% Swarm Neutralized:</span>
<span className="text-primary-container font-telemetry-data text-telemetry-data font-bold">PASS-GRADE A</span>
</div>
</div>
</div>
</div>
{/*  ==========================================  */}
{/*  COLUMN 2: Tactical Ingress Vectors & Map    */}
{/*  ==========================================  */}
<div className="lg:col-span-5 flex flex-col gap-space-sm">
{/*  Map Header & Coordinate Reference  */}
<div className="p-space-sm bg-surface-container-low flex flex-wrap items-center justify-between gap-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-secondary-container">radar</span>
<span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface font-bold">TACTICAL VECTOR SCRIPTING // TOP-DOWN PROJECTION</span>
</div>
<div className="flex items-center gap-space-sm text-on-surface-variant font-label-sm text-label-sm">
<span>CENTER: <strong className="text-on-surface">DEF-ALPHA (0,0)</strong></span>
<span>SCALE: <strong className="text-secondary-container">1:25000</strong></span>
<span>GRID: <strong className="text-on-surface">MGRS-WGS84</strong></span>
</div>
</div>
{/*  Vector Editing Canvas Container  */}
<div className="relative w-full bg-surface-container-lowest h-[480px] overflow-hidden flex items-center justify-center">
{/*  Subtle Tactical Background Radar Screen using SVG  */}
<svg className="absolute inset-0 w-full h-full pointer-events-none text-outline-variant opacity-60" fill="none" viewBox="0 0 600 480" xmlns="http://www.w3.org/2000/svg">
{/*  Background Grid Lines  */}
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="0" x2="600" y1="120" y2="120"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="0" x2="600" y1="240" y2="240"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="0" x2="600" y1="360" y2="360"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="150" x2="150" y1="0" y2="480"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="300" x2="300" y1="0" y2="480"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.7" x1="450" x2="450" y1="0" y2="480"></line>
{/*  Range Rings Centered at (300, 240)  */}
<circle cx="300" cy="240" r="60" stroke="currentColor" strokeWidth="0.8"></circle>
<circle cx="300" cy="240" r="120" stroke="currentColor" strokeDasharray="4 4" strokeWidth="0.8"></circle>
<circle cx="300" cy="240" r="180" stroke="currentColor" strokeWidth="0.8"></circle>
<circle cx="300" cy="240" r="230" stroke="currentColor" strokeDasharray="6 6" strokeWidth="0.8"></circle>
{/*  Bearing Radials  */}
<line stroke="currentColor" strokeWidth="0.5" x1="300" x2="300" y1="10" y2="470"></line>
<line stroke="currentColor" strokeWidth="0.5" x1="70" x2="530" y1="240" y2="240"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.5" x1="137" x2="463" y1="77" y2="403"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="0.5" x1="137" x2="463" y1="403" y2="77"></line>
{/*  Range Ring Labels  */}
<text fill="#849581" font-family="Space Mono" font-size="8" x="306" y="176">500M</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="306" y="116">1500M</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="306" y="56">3000M INNER RING</text>
<text fill="#00ff66" font-family="Space Mono" font-size="9" font-weight="bold" x="292" y="24">000° N</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="540" y="244">090° E</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="292" y="475">180° S</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="35" y="244">270° W</text>
{/*  EW Jamming Wedge Overlay (030° to 070°)  */}
<path d="M 300 240 L 490 70 A 230 230 0 0 1 526 185 Z" fill="#00e3fd" fillOpacity="0.12" stroke="#00e3fd" strokeDasharray="4 2" strokeWidth="1"></path>
<text fill="#00e3fd" font-family="Space Mono" font-size="8" font-weight="bold" x="445" y="115">EW STROBE SECTOR 02</text>
<text fill="#bdf4ff" font-family="Space Mono" font-size="7" x="445" y="127">PMR: 4.8 KW // NOISE FLOOD</text>
{/*  Attack Vector Alpha (Bearing 045° - Crimson)  */}
<path d="M 480 60 L 410 130 L 355 185 L 300 240" fill="none" stroke="#ff3344" strokeDasharray="5 3" strokeWidth="2.5"></path>
{/*  Waypoint Markers for Vector Alpha  */}
{/*  WP-01 Ingress  */}
<circle cx="480" cy="60" fill="#121316" r="5" stroke="#ff3344" strokeWidth="2"></circle>
<text fill="#ff3344" font-family="Space Mono" font-size="9" font-weight="bold" x="490" y="64">WP-01 [SPAWN 045°]</text>
{/*  WP-02 Split Altitude  */}
<circle cx="410" cy="130" fill="#121316" r="5" stroke="#ff3344" strokeWidth="2"></circle>
<text fill="#ffb4ab" font-family="Space Mono" font-size="8" x="420" y="134">WP-02 [SPLIT 150M]</text>
{/*  WP-03 Terminal Dive (Selected)  */}
<circle cx="355" cy="185" fill="#ff3344" fillOpacity="0.3" r="7" stroke="#00ff66" strokeWidth="2"></circle>
<circle cx="355" cy="185" fill="#00ff66" r="3"></circle>
<text fill="#00ff66" font-family="Space Mono" font-size="9" font-weight="bold" x="368" y="187">WP-03 [SEL]</text>
{/*  Attack Vector Bravo (Bearing 120° - Amber)  */}
<path d="M 520 330 L 420 300 L 340 270 L 300 240" fill="none" stroke="#ffd7aa" strokeDasharray="3 3" strokeWidth="2"></path>
<circle cx="520" cy="330" fill="#121316" r="4" stroke="#ffd7aa" strokeWidth="1.5"></circle>
<text fill="#ffd7aa" font-family="Space Mono" font-size="8" x="440" y="348">VECTOR BRAVO [6x FPV 120°]</text>
{/*  Target Base Center Icon (DEF-ALPHA)  */}
<rect fill="#003911" height="20" stroke="#00ff66" strokeWidth="1.5" width="20" x="290" y="230"></rect>
<circle cx="300" cy="240" fill="#edffe8" r="2"></circle>
<text fill="#00ff66" font-family="Space Mono" font-size="9" font-weight="bold" x="260" y="265">DEF-ALPHA [HQ]</text>
<text fill="#849581" font-family="Space Mono" font-size="7" x="254" y="275">ELEV: 320m // SAM-RADAR</text>
{/*  Loitering Decoy Pattern in Sector 4  */}
<ellipse cx="180" cy="150" fill="none" rx="40" ry="25" stroke="#bdf4ff" strokeDasharray="2 3" strokeWidth="1"></ellipse>
<text fill="#bdf4ff" font-family="Space Mono" font-size="7" x="145" y="145">ORBIT: DECOY FLOCK</text>
</svg>
{/*  Dynamic Overlay Tactical HUD Badges  */}
<div className="absolute top-space-sm left-space-sm bg-surface-container-high/90 backdrop-blur px-space-sm py-space-xs flex flex-col gap-space-xs">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 rounded-full bg-error animate-ping"></span>
<span className="text-error font-label-sm text-label-sm font-bold uppercase">INGRESS SIMULATION: WAVE 02</span>
</div>
<span className="text-on-surface-variant font-label-sm text-label-sm">PRIMARY VECTOR ALPHA (6x FPV)</span>
<span className="text-on-surface-variant font-label-sm text-label-sm">FLANK VECTOR BRAVO (6x FPV)</span>
</div>
<div className="absolute top-space-sm right-space-sm bg-surface-container-high/90 backdrop-blur px-space-sm py-space-xs text-right">
<div className="text-primary-container font-telemetry-data text-telemetry-data">38.4192° N</div>
<div className="text-secondary-container font-telemetry-data text-telemetry-data">042.8812° E</div>
<div className="text-on-surface-variant font-label-sm text-label-sm">BARO: 1013.2 HPA</div>
</div>
{/*  Waypoint Context Bubble on Active WP-03  */}
<div className="absolute top-[138px] left-[325px] bg-surface-container-highest px-space-sm py-space-xs shadow-lg flex flex-col gap-0.5 pointer-events-none">
<div className="flex items-center justify-between gap-space-md">
<span className="text-primary-container font-label-sm text-label-sm font-bold">WP-03 (DIVE-ENTRY)</span>
<span className="text-on-surface-variant font-label-sm text-label-sm">T+05:40</span>
</div>
<div className="text-on-surface font-label-sm text-label-sm">ALT: 150m → 25m TERRAIN HUG</div>
<div className="text-secondary font-label-sm text-label-sm">SPEED: 140 KTS DIVE</div>
</div>
{/*  Map Coordinate Crosshairs in Center Target  */}
<div className="absolute bottom-space-sm left-space-sm flex items-center gap-space-xs bg-surface-container-high/90 px-space-sm py-space-xs font-label-sm text-label-sm text-on-surface-variant">
<span className="material-symbols-outlined text-[14px] text-primary-container">near_me</span>
<span>CURSOR POS: 38TLN 4429 8812 // ELEV: 182M</span>
</div>
</div>
{/*  Vector & Waypoint Inspector Strip  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-sm">
<div className="flex flex-wrap items-center justify-between gap-space-sm bg-surface-container p-space-xs">
{/*  Waypoint Selector Tabs  */}
<div className="flex items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase px-space-xs">SELECT WAYPOINT:</span>
<button className="px-space-sm py-space-xs bg-surface-container-high text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">WP-01</button>
<button className="px-space-sm py-space-xs bg-surface-container-high text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">WP-02</button>
<button className="px-space-sm py-space-xs bg-primary-container text-on-primary-container font-label-sm text-label-sm font-bold uppercase shadow-sm" type="button">WP-03 (ACTIVE)</button>
<button className="px-space-sm py-space-xs bg-surface-container-highest text-primary-container hover:bg-surface-bright font-label-sm text-label-sm uppercase" type="button">+ WP</button>
</div>
<div className="flex items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant">WAYPOINT TIME:</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container">T+05:40.00</span>
</div>
</div>
{/*  Waypoint Parameter Form Controls  */}
<div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm">
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">ALTITUDE AGL</label>
<div className="flex items-center justify-between">
<input className="bg-transparent font-telemetry-data text-telemetry-data text-primary w-16 focus:outline-none" type="text" value="150"/>
<span className="font-label-sm text-label-sm text-on-surface-variant">METERS</span>
</div>
</div>
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">INGRESS SPEED</label>
<div className="flex items-center justify-between">
<input className="bg-transparent font-telemetry-data text-telemetry-data text-primary w-16 focus:outline-none" type="text" value="120"/>
<span className="font-label-sm text-label-sm text-on-surface-variant">KNOTS</span>
</div>
</div>
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">TRAJECTORY TYPE</label>
<select className="bg-surface-container-highest font-label-sm text-label-sm text-secondary-container p-0.5 focus:outline-none">
<option selected="">WEAVING DIVE</option>
<option>LINEAR INTERCEPT</option>
<option>TERRAIN CLING</option>
<option>SPIRAL POP-UP</option>
</select>
</div>
<div className="flex flex-col gap-space-xs bg-surface-container-lowest p-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">TERMINAL BEHAVIOR</label>
<select className="bg-surface-container-highest font-label-sm text-label-sm text-error p-0.5 focus:outline-none">
<option selected="">KINETIC STRIKE</option>
<option>AIRBURST SHRAPNEL</option>
<option>LOITER RE-ENGAGE</option>
<option>SELF-DESTRUCT RF</option>
</select>
</div>
</div>
{/*  Tactical Toolbox Strip  */}
<div className="flex flex-wrap items-center justify-between gap-space-xs pt-space-xs">
<div className="flex flex-wrap items-center gap-space-xs">
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[14px] text-primary-container">route</span>
<span>ADD WAYPOINT</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[14px] text-error">timeline</span>
<span>DRAW INGRESS</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[14px] text-secondary-container">wifi_tethering_error</span>
<span>JAMMER STROBE</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[14px] text-tertiary-fixed-dim">grain</span>
<span>DECOY FLOCK</span>
</button>
</div>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-highest hover:bg-error-container text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[14px] text-error">delete_outline</span>
<span>CLEAR WP</span>
</button>
</div>
</div>
</div>
{/*  ==========================================  */}
{/*  COLUMN 3: Swarm Behavior & Inject Params    */}
{/*  ==========================================  */}
<div className="lg:col-span-4 flex flex-col gap-space-sm">
{/*  Card 1: Selected Wave Detailed Config  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-md">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest p-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-primary-container">tune</span>
<span className="font-label-sm text-label-sm uppercase font-bold text-on-surface">SWARM AI &amp; PAYLOAD SPECS</span>
</div>
<span className="text-primary-container font-label-sm text-label-sm font-bold uppercase">WAVE 02 ACTIVE</span>
</div>
{/*  Drone Sub-Type Selector Pills  */}
<div className="flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">THREAT AIRFRAME CLASS</span>
<div className="grid grid-cols-2 gap-space-xs">
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container-highest text-primary-container font-label-sm text-label-sm font-bold uppercase shadow-sm" type="button">
<span className="w-1.5 h-1.5 bg-primary-container"></span>
<span>FPV KAMIKAZE (3KG)</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm uppercase" type="button">
<span className="w-1.5 h-1.5 bg-outline"></span>
<span>MICRO-QUAD SWARM</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm uppercase" type="button">
<span className="w-1.5 h-1.5 bg-outline"></span>
<span>FIXED-WING EW LOITER</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm uppercase" type="button">
<span className="w-1.5 h-1.5 bg-outline"></span>
<span>AUTONOMOUS DECOY</span>
</button>
</div>
</div>
{/*  Swarm Intelligence AI Parameters  */}
<div className="flex flex-col gap-space-sm bg-surface-container-lowest p-space-sm">
<span className="font-label-sm text-label-sm text-primary-container font-bold uppercase tracking-wider">AUTONOMOUS SWARM BEHAVIOR LOGIC</span>
{/*  Formation Geometry  */}
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant uppercase">FORMATION GEOMETRY</span>
<span className="text-secondary-container font-bold">SATURATION CLOUD</span>
</div>
<div className="grid grid-cols-4 gap-space-xs">
<button className="py-space-xs bg-surface-container text-on-surface-variant text-center font-label-sm text-label-sm hover:text-on-surface" type="button">VEE</button>
<button className="py-space-xs bg-secondary-container text-on-secondary-container font-bold text-center font-label-sm text-label-sm" type="button">CLOUD</button>
<button className="py-space-xs bg-surface-container text-on-surface-variant text-center font-label-sm text-label-sm hover:text-on-surface" type="button">PINCH</button>
<button className="py-space-xs bg-surface-container text-on-surface-variant text-center font-label-sm text-label-sm hover:text-on-surface" type="button">LEAD-FOL</button>
</div>
</div>
{/*  Evasive Maneuver Algorithm  */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">EVASIVE KINEMATICS</label>
<div className="flex items-center justify-between bg-surface-container-high p-space-xs text-label-sm font-label-sm">
<span className="text-on-surface">AGGRESSIVE 4G RANDOMIZED WEAVE</span>
<span className="material-symbols-outlined text-[16px] text-primary-container">check_circle</span>
</div>
</div>
{/*  Mesh Redundancy  */}
<div className="flex flex-col gap-space-xs">
<label className="font-label-sm text-label-sm text-on-surface-variant uppercase">INTER-DRONE MESH PROTOCOL</label>
<div className="flex items-center justify-between bg-surface-container-high p-space-xs text-label-sm font-label-sm">
<span className="text-on-surface">AD-HOC MESH (RE-LEADER ON LOSS)</span>
<span className="text-primary-container font-telemetry-data text-telemetry-data">ACTIVE</span>
</div>
</div>
</div>
{/*  Environmental & Electronic Injects for this Wave  */}
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-bold">ATMOSPHERIC &amp; EW INJECTS</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim">3 MODIFIERS ENABLED</span>
</div>
<div className="flex flex-col gap-space-xs">
<div className="flex items-center justify-between bg-surface-container-lowest p-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[14px] text-tertiary-fixed-dim">air</span>
<span className="font-body-sm text-body-sm text-on-surface">Microburst Shear at T+04:15 (28 kts crosswind)</span>
</div>
<span className="text-primary-container font-label-sm text-label-sm">ON</span>
</div>
<div className="flex items-center justify-between bg-surface-container-lowest p-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[14px] text-secondary-container">foggy</span>
<span className="font-body-sm text-body-sm text-on-surface">Optics Degrade: Ground Fog Influx (+45% obscuration)</span>
</div>
<span className="text-primary-container font-label-sm text-label-sm">ON</span>
</div>
<div className="flex items-center justify-between bg-surface-container-lowest p-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[14px] text-primary-container">wifi_protected_setup</span>
<span className="font-body-sm text-body-sm text-on-surface">FHSS Anti-Jam Protocol (120 hops/sec)</span>
</div>
<span className="text-primary-container font-label-sm text-label-sm">ON</span>
</div>
</div>
</div>
</div>
{/*  Card 2: Trainee Evaluation Stressors & Rubric Injects  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-sm">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest p-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-error">assignment_late</span>
<span className="font-label-sm text-label-sm uppercase font-bold text-on-surface">OPERATOR STRESS TESTS // RUBRIC</span>
</div>
<span className="text-error font-label-sm text-label-sm font-bold">2 ACTIVE INJECTS</span>
</div>
{/*  Stressor 1: False Flag IFF Trap  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<span className="text-error font-label-sm text-label-sm font-bold uppercase">STRESS TRAP #1 // SPOOFED IFF</span>
<span className="px-space-xs py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold">CRITICAL</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface">Inject spoofed Friendly Mode-4 IFF transponder pulses on 1x hostile FPV drone (Ghost Track). Evaluates operator cross-verification via optical vs RF radar before clearance.</p>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm pt-space-xs">
<span>TRIGGER TIMING: <strong className="text-on-surface">T+04:45</strong></span>
<span>PENALTY: <strong className="text-error">-25 PTS IF MISIDENTIFIED</strong></span>
</div>
</div>
{/*  Stressor 2: Reaction Latency Cutoff  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<span className="text-tertiary-fixed-dim font-label-sm text-label-sm font-bold uppercase">STRESS TRAP #2 // SENSOR SATURATION</span>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-tertiary-fixed font-label-sm text-label-sm">EVAL</span>
</div>
<p className="font-body-sm text-body-sm text-on-surface">Operator reaction window threshold: Engagement decision required within <strong>3.50 seconds</strong> upon perimeter threshold cross (2,000m barrier).</p>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm pt-space-xs">
<span>FAIL ACTION: <strong className="text-on-surface">SOUND KINETIC SIREN</strong></span>
<span>TOLERANCE: <strong className="text-primary-container">±0.5 SEC</strong></span>
</div>
</div>
</div>
</div>
</div>
{/*  ==========================================  */}
{/*  BOTTOM TIMELINE SCRUBBER & SEQUENCER BAR    */}
{/*  ==========================================  */}
<div className="w-full bg-surface-container-lowest p-space-md flex flex-col gap-space-sm shadow-xl">
{/*  Timeline Header & Time Readout  */}
<div className="flex flex-wrap items-center justify-between gap-space-sm">
<div className="flex items-center gap-space-md">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px] text-primary-container">history_toggle_off</span>
<span className="font-label-md text-label-md text-on-surface font-bold uppercase">SCENARIO MASTER TIMELINE SCRUBBER</span>
</div>
<div className="flex items-center gap-space-xs bg-surface-container-high px-space-sm py-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SIM TIME:</span>
<span className="font-telemetry-critical text-telemetry-critical text-primary-container" id="currentSimTime">T+05:22.40</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">/ 18:00.00</span>
</div>
</div>
{/*  Playback Controls  */}
<div className="flex items-center gap-space-xs">
<button className="p-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface" onclick="scrubTo(0)" title="Jump to Beginning" type="button">
<span className="material-symbols-outlined text-[16px]">skip_previous</span>
</button>
<button className="p-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface" onclick="adjustTime(-10)" title="Step Back 10s" type="button">
<span className="material-symbols-outlined text-[16px]">replay_10</span>
</button>
<button className="px-space-md py-space-xs bg-primary-container text-on-primary-container font-bold flex items-center gap-space-xs" id="playBtn" onclick="togglePlay()" type="button">
<span className="material-symbols-outlined text-[16px]" id="playIcon">pause</span>
<span className="font-label-sm text-label-sm uppercase" id="playLabel">PAUSE</span>
</button>
<button className="p-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface" onclick="adjustTime(10)" title="Step Forward 10s" type="button">
<span className="material-symbols-outlined text-[16px]">forward_10</span>
</button>
<button className="p-space-xs bg-surface-container hover:bg-surface-container-high text-on-surface" onclick="scrubTo(1080)" title="Jump to End" type="button">
<span className="material-symbols-outlined text-[16px]">skip_next</span>
</button>
<div className="h-4 w-px bg-outline-variant mx-space-xs"></div>
{/*  Playback Rate Pill  */}
<div className="flex items-center bg-surface-container">
<button className="px-space-xs py-space-xs text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm" type="button">1X</button>
<button className="px-space-xs py-space-xs bg-primary text-on-primary font-bold font-label-sm text-label-sm" type="button">2X</button>
<button className="px-space-xs py-space-xs text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm" type="button">4X</button>
</div>
<button className="flex items-center gap-space-xs px-space-sm py-space-xs bg-surface-container hover:bg-surface-container-high text-secondary-container font-label-sm text-label-sm uppercase ml-space-xs" type="button">
<span className="material-symbols-outlined text-[14px]">volume_up</span>
<span>CUE AUDIO</span>
</button>
</div>
</div>
{/*  Graphical Timeline Track Container  */}
<div className="relative w-full bg-surface-container-high h-14 overflow-hidden select-none cursor-pointer" id="timelineTrack" onclick="handleTrackClick(event)">
{/*  Background 1-Minute Tick Grid  */}
<div className="absolute inset-0 flex justify-between pointer-events-none opacity-30">
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
<div className="w-px h-full bg-outline"></div>
</div>
{/*  Wave Phase Segments Blocks  */}
<div className="absolute inset-y-1.5 left-0 right-0 flex gap-0.5 px-0.5">
{/*  Wave 1: 0 to 3.5m (19.4% width)  */}
<div className="h-full bg-surface-container flex flex-col justify-between p-1 relative overflow-hidden group hover:brightness-110" >
<div className="flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface font-bold truncate">WAVE 01: RECON</span>
<span className="text-on-surface-variant font-telemetry-data text-telemetry-data text-[10px]">03:30</span>
</div>
<div className="w-full bg-primary h-1 opacity-60"></div>
</div>
{/*  Wave 2: 3.5m to 8m (25% width) - ACTIVE  */}
<div className="h-full bg-surface-container-highest flex flex-col justify-between p-1 relative overflow-hidden ring-1 ring-primary-container group hover:brightness-110" >
<div className="flex items-center justify-between text-label-sm font-label-sm">
<span className="text-primary-container font-bold truncate">WAVE 02: FPV SATURATION</span>
<span className="text-primary-container font-telemetry-data text-telemetry-data text-[10px]">08:00</span>
</div>
<div className="w-full bg-primary-container h-1 shadow-[0_0_8px_#00ff66]"></div>
</div>
{/*  Wave 3: 8m to 14m (33.3% width)  */}
<div className="h-full bg-surface-container flex flex-col justify-between p-1 relative overflow-hidden group hover:brightness-110" >
<div className="flex items-center justify-between text-label-sm font-label-sm">
<span className="text-tertiary-fixed-dim font-bold truncate">WAVE 03: PINCH ATTACK</span>
<span className="text-on-surface-variant font-telemetry-data text-telemetry-data text-[10px]">14:00</span>
</div>
<div className="w-full bg-tertiary-fixed-dim h-1 opacity-70"></div>
</div>
{/*  Wave 4: 14m to 18m (22.3% width)  */}
<div className="h-full bg-surface-container flex flex-col justify-between p-1 relative overflow-hidden group hover:brightness-110" >
<div className="flex items-center justify-between text-label-sm font-label-sm">
<span className="text-error font-bold truncate">WAVE 04: HEAVY KINETIC</span>
<span className="text-on-surface-variant font-telemetry-data text-telemetry-data text-[10px]">18:00</span>
</div>
<div className="w-full bg-error h-1 opacity-70"></div>
</div>
</div>
{/*  Specific Discrete Event Inject Markers along timeline  */}
{/*  T+02:15 Chaff Strobe (12.5% pos)  */}
<div className="absolute top-0 bottom-0 left-[12.5%] w-px bg-secondary-container pointer-events-none z-10">
<span className="absolute -top-0.5 -left-1.5 w-3 h-3 bg-secondary-container transform rotate-45"></span>
<div className="absolute bottom-1 -left-10 bg-surface-container-highest px-1 text-[8px] font-label-sm text-secondary-container whitespace-nowrap shadow">T+02:15 CHAFF</div>
</div>
{/*  T+04:00 Swarm Spawn (22.2% pos)  */}
<div className="absolute top-0 bottom-0 left-[22.2%] w-px bg-primary-container pointer-events-none z-10">
<span className="absolute -top-0.5 -left-1.5 w-3 h-3 bg-primary-container transform rotate-45"></span>
<div className="absolute top-1 -left-12 bg-surface-container-highest px-1 text-[8px] font-label-sm text-primary-container whitespace-nowrap shadow">T+04:00 SPAWN</div>
</div>
{/*  T+06:30 Trainee Radar Jam (36.1% pos)  */}
<div className="absolute top-0 bottom-0 left-[36.1%] w-px bg-tertiary-fixed-dim pointer-events-none z-10">
<span className="absolute -top-0.5 -left-1.5 w-3 h-3 bg-tertiary-fixed-dim transform rotate-45"></span>
<div className="absolute bottom-1 -left-12 bg-surface-container-highest px-1 text-[8px] font-label-sm text-tertiary-fixed-dim whitespace-nowrap shadow">T+06:30 JAMMER</div>
</div>
{/*  T+11:00 Saturation Influx (61.1% pos)  */}
<div className="absolute top-0 bottom-0 left-[61.1%] w-px bg-error pointer-events-none z-10">
<span className="absolute -top-0.5 -left-1.5 w-3 h-3 bg-error transform rotate-45"></span>
<div className="absolute bottom-1 -left-14 bg-surface-container-highest px-1 text-[8px] font-label-sm text-error whitespace-nowrap shadow">T+11:00 MASS SAT</div>
</div>
{/*  Playhead Needle (At 05:22 = 322s / 1080s = ~29.8% position)  */}
<div className="absolute top-0 bottom-0 w-1 bg-primary-container z-20 pointer-events-none shadow-[0_0_10px_#00ff66]" id="playhead" >
<div className="w-3 h-3 bg-primary-container transform rotate-45 -ml-1 -mt-1 shadow-md"></div>
<div className="w-3 h-3 bg-primary-container transform rotate-45 -ml-1 absolute bottom-0 shadow-md"></div>
</div>
</div>
{/*  Timeline Axis Time Scale Marks  */}
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm px-1">
<span>T+00:00</span>
<span>T+02:00</span>
<span>T+04:00</span>
<span className="text-primary-container font-bold">T+06:00</span>
<span>T+08:00</span>
<span>T+10:00</span>
<span>T+12:00</span>
<span>T+14:00</span>
<span>T+16:00</span>
<span>T+18:00 (MAX)</span>
</div>
</div>
{/*  Interactive Simulation Timeline Scrubbing Script  */}

</div></main></div>
    </div>
  );
}
