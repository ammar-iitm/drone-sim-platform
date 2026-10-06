import React from 'react';

export default function LiveDashboard() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs" data-active-classes="bg-surface-container text-primary-container font-bold border-l-2 border-primary-container"><a aria-current="page" className="flex items-center gap-space-md px-space-md py-space-md transition-all uppercase bg-surface-container text-primary-container font-bold border-l-2 border-primary-container" data-path="live-dashboard" href="#"><span className="material-symbols-outlined text-[18px]">grid_view</span><span>Live Dashboard</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span className="material-symbols-outlined text-[18px]">alt_route</span><span>Scenario Builder</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="aar-reports" href="#"><span className="material-symbols-outlined text-[18px]">summarize</span><span>AAR Reports</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="unit-roster" href="#"><span className="material-symbols-outlined text-[18px]">shield_person</span><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
{/*  TOP OPERATIONAL BAR  */}
<section className="bg-surface-container-low px-space-md py-space-sm mb-space-sm flex flex-wrap items-center justify-between gap-y-space-sm">
{/*  Trainee Profile & Exercise Context  */}
<div className="flex items-center gap-space-lg flex-wrap">
<div className="flex items-center gap-space-sm">
<span className="w-2.5 h-2.5 bg-primary-container"></span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EVALUATION SUBJECT</span>
<span className="font-label-lg text-label-lg text-primary uppercase">LT. J. MILLER <span className="text-on-surface-variant font-label-sm text-label-sm">[ID: TRN-8842]</span></span>
</div>
<span className="px-space-sm py-space-xs bg-surface-container-high text-primary-container font-label-sm text-label-sm uppercase ml-space-xs">
          ACTIVE EVALUATION
        </span>
</div>
<div className="h-6 w-px bg-surface-container-highest hidden md:block"></div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">MISSION CODE // EXERCISE ID</span>
<span className="font-label-md text-label-md text-on-surface uppercase">SIM-EX-2025-048 • HYBRID SWARM INTRUSION (PHASE 2)</span>
</div>
<div className="h-6 w-px bg-surface-container-highest hidden md:block"></div>
{/*  Live Sim Timer  */}
<div className="flex items-center gap-space-sm bg-surface-container-lowest px-space-md py-space-xs">
<span className="w-2 h-2 rounded-full bg-primary-container animate-ping"></span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SIM ELAPSED</span>
<span className="font-telemetry-critical text-telemetry-critical text-primary-container" id="sim-timer">00:14:38.4</span>
</div>
<span className="font-label-sm text-label-sm bg-surface-container-high text-secondary-fixed px-space-xs py-space-xs uppercase ml-space-xs">1.0X REALTIME</span>
</div>
</div>
{/*  Base Health & Tactical Instructor Interventions  */}
<div className="flex items-center gap-space-lg flex-wrap">
<div className="flex flex-col min-w-[180px]">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mb-space-xs">
<span className="uppercase">BASE DEFENSE INTEGRITY</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">78% [SECTOR BOMBARDED]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative overflow-hidden">
<div className="bg-primary-container h-full transition-all duration-300" ></div>
<div className="absolute left-1/4 top-0 bottom-0 w-0.5 bg-error opacity-40"></div>
<div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-tertiary-fixed-dim opacity-40"></div>
</div>
</div>
{/*  Global Actions  */}
<div className="flex items-center gap-space-xs">
<button className="px-space-md py-space-xs bg-surface-container text-on-surface hover:bg-surface-container-high active:bg-surface-container-highest text-label-md font-label-md uppercase transition-colors flex items-center gap-space-xs" id="btn-pause-sim" type="button">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">pause</span>
<span>PAUSE</span>
</button>
<button className="px-space-md py-space-xs bg-surface-container text-on-surface hover:bg-surface-container-high active:bg-surface-container-highest text-label-md font-label-md uppercase transition-colors flex items-center gap-space-xs" id="btn-reset-sim" type="button">
<span className="material-symbols-outlined text-[16px] text-secondary-fixed">restart_alt</span>
<span>RESET</span>
</button>
<button className="px-space-md py-space-xs bg-error-container text-error hover:bg-on-error hover:text-error-container text-label-md font-label-md uppercase transition-colors flex items-center gap-space-xs" id="btn-abort-sim" type="button">
<span className="material-symbols-outlined text-[16px]">warning</span>
<span>ABORT</span>
</button>
</div>
</div>
</section>
{/*  WORKSPACE GRID: 24 Columns High-Density Layout  */}
<div className="grid grid-cols-1 lg:grid-cols-24 gap-space-sm px-space-md pb-space-lg">
{/*  LEFT COLUMN: RADAR C2 & EVENT LOG (Cols 1 to 15)  */}
<div className="lg:col-span-15 flex flex-col gap-space-sm">
{/*  RADAR SECTION  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col">
{/*  Panel Header  */}
<div className="flex items-center justify-between pb-space-xs mb-space-sm bg-surface-container-lowest px-space-sm py-space-xs">
<div className="flex items-center gap-space-sm">
<span className="font-label-sm text-label-sm text-secondary-container font-bold uppercase">DISP // RADAR 2D TACTICAL C2</span>
<span className="px-space-xs py-0.5 bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm">BAND-X ACTIVE</span>
</div>
<div className="flex items-center gap-space-md font-label-sm text-label-sm text-on-surface-variant">
<span>GRID: <strong className="text-on-surface font-telemetry-data text-telemetry-data font-normal">38S MB 4482 1290</strong></span>
<span>ELEV: <strong className="text-on-surface font-telemetry-data text-telemetry-data font-normal">412m MSL</strong></span>
<span className="text-primary-container font-bold">RADAR-LOCK: FULL DOMAIN</span>
</div>
</div>
{/*  Radar Canvas Container  */}
<div className="relative w-full aspect-[16/10] bg-surface-container-lowest overflow-hidden flex items-center justify-center">
{/*  Tactical Overlay Canvas (Interactive / Animated)  */}
<svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="xMidYMid meet" viewBox="0 0 800 500">
<defs>
<radialgradient cx="50%" cy="50%" id="radarSweepGlow" r="50%">
<stop offset="0%" stopColor="#00FF66" stopOpacity="0.12"></stop>
<stop offset="70%" stopColor="#00FF66" stopOpacity="0.04"></stop>
<stop offset="100%" stopColor="#00FF66" stopOpacity="0"></stop>
</radialgradient>
<lineargradient id="sweepLineGrad" x1="0%" x2="100%" y1="0%" y2="100%">
<stop offset="0%" stopColor="#00FF66" stopOpacity="0.8"></stop>
<stop offset="100%" stopColor="#00FF66" stopOpacity="0"></stop>
</lineargradient>
</defs>
{/*  Orthogonal Grid lines  */}
<g stroke="#1F2420" strokeDasharray="2 4" strokeWidth="0.75">
<line x1="50" x2="50" y1="0" y2="500"></line>
<line x1="150" x2="150" y1="0" y2="500"></line>
<line x1="250" x2="250" y1="0" y2="500"></line>
<line x1="350" x2="350" y1="0" y2="500"></line>
<line x1="450" x2="450" y1="0" y2="500"></line>
<line x1="550" x2="550" y1="0" y2="500"></line>
<line x1="650" x2="650" y1="0" y2="500"></line>
<line x1="750" x2="750" y1="0" y2="500"></line>
<line x1="0" x2="800" y1="50" y2="50"></line>
<line x1="0" x2="800" y1="125" y2="125"></line>
<line x1="0" x2="800" y1="200" y2="200"></line>
<line x1="0" x2="800" y1="300" y2="300"></line>
<line x1="0" x2="800" y1="375" y2="375"></line>
<line x1="0" x2="800" y1="450" y2="450"></line>
</g>
{/*  Primary Crosshairs intersecting at (400, 250)  */}
<line stroke="#2D3A30" strokeWidth="1" x1="400" x2="400" y1="10" y2="490"></line>
<line stroke="#2D3A30" strokeWidth="1" x1="10" x2="790" y1="250" y2="250"></line>
{/*  Polar Concentric Range Rings (origin 400, 250)  */}
{/*  500m  */}
<circle cx="400" cy="250" fill="none" r="55" stroke="#223326" strokeDasharray="3 3" strokeWidth="1"></circle>
<text fill="#849581" font-family="Space Mono" font-size="9" x="405" y="198">500M</text>
{/*  1km  */}
<circle cx="400" cy="250" fill="none" r="110" stroke="#29402E" strokeWidth="1"></circle>
<text fill="#849581" font-family="Space Mono" font-size="9" x="405" y="143">1000M</text>
{/*  2km  */}
<circle cx="400" cy="250" fill="none" r="175" stroke="#223326" strokeDasharray="4 4" strokeWidth="1"></circle>
<text fill="#849581" font-family="Space Mono" font-size="9" x="405" y="78">2000M</text>
{/*  3km Perimeter  */}
<circle cx="400" cy="250" fill="none" r="235" stroke="#2F4D36" strokeWidth="1.25"></circle>
<text fill="#849581" font-family="Space Mono" font-size="9" x="405" y="20">3000M MAX RNG</text>
{/*  Cardinal Bearings  */}
<text fill="#00FF66" font-family="Space Mono" font-size="10" font-weight="bold" text-anchor="middle" x="400" y="12">000° [N]</text>
<text fill="#849581" font-family="Space Mono" font-size="10" text-anchor="end" x="785" y="253">090° [E]</text>
<text fill="#849581" font-family="Space Mono" font-size="10" text-anchor="middle" x="400" y="492">180° [S]</text>
<text fill="#849581" font-family="Space Mono" font-size="10" text-anchor="start" x="15" y="253">270° [W]</text>
{/*  Rotating Radar Sweep Line  */}
<g transform="translate(400, 250)">
<line stroke="url(#sweepLineGrad)" strokeWidth="2" x1="0" x2="235" y1="0" y2="0">
<a href="#"nimateTransform attributename="transform" dur="4.8s" from="0" repeatcount="indefinite" to="360" type="rotate" /></animatetransform>
</line>
</g>
{/*  Jamming Sector Visualization (Sector NW 285°-330°)  */}
<path d="M 400 250 L 210 110 A 235 235 0 0 1 290 60 Z" fill="#FFB4AB" fillOpacity="0.08" id="jamming-cone" stroke="#93000A" strokeDasharray="2 3" strokeWidth="0.75"></path>
<text fill="#FFB4AB" font-family="Space Mono" font-size="8" opacity="0.8" x="240" y="120">JAMMED SECTOR 4A</text>
{/*  Threat Corridors Overlay (Vector lanes)  */}
<path d="M 680 70 L 520 160 L 400 250" fill="none" stroke="#FFB4AB" strokeDasharray="4 6" strokeOpacity="0.3" strokeWidth="1.5"></path>
<path d="M 120 380 L 290 310 L 400 250" fill="none" stroke="#FFB4AB" strokeDasharray="4 6" strokeOpacity="0.3" strokeWidth="1.5"></path>
{/*  CENTER DEFENSE ARRAY (TRAINEE POSITION)  */}
<circle cx="400" cy="250" fill="#00FF66" fillOpacity="0.12" r="14"></circle>
<circle cx="400" cy="250" fill="#00FF66" r="4"></circle>
<circle cx="400" cy="250" fill="none" r="9" stroke="#00FF66" strokeWidth="1">
<a href="#"nimate attributename="r" dur="2s" repeatcount="indefinite" values="4;18;4" /></animate>
<a href="#"nimate attributename="opacity" dur="2s" repeatcount="indefinite" values="0.8;0;0.8" /></animate>
</circle>
{/*  Center Label  */}
<rect fill="#0D0E11" fillOpacity="0.9" height="15" width="110" x="345" y="260"></rect>
<text fill="#00FF66" font-family="Space Mono" font-size="9" font-weight="bold" text-anchor="middle" x="400" y="271">DEF-ALPHA [TRAINEE]</text>
{/*  HOSTILE TARGET BLIP 1 (FPV Kamikaze Fast)  */}
<g className="cursor-pointer" id="blip-tgt01">
{/*  Velocity vector line  */}
<line stroke="#FFB4AB" strokeWidth="1.5" x1="570" x2="520" y1="130" y2="160"></line>
{/*  Hostile Icon: Solid Diamond  */}
<polygon fill="#93000A" points="570,125 575,130 570,135 565,130" stroke="#FFB4AB" strokeWidth="1"></polygon>
<circle cx="570" cy="130" fill="none" r="9" stroke="#FFB4AB" strokeDasharray="2 2" strokeWidth="0.75"></circle>
{/*  HUD Label Box  */}
<rect fill="#1F1F23" fillOpacity="0.9" height="28" width="165" x="582" y="115"></rect>
<text fill="#FFB4AB" font-family="Space Mono" font-size="9" font-weight="bold" x="586" y="127">TGT-01: FPV KAMIKAZE</text>
<text fill="#E3E2E6" font-family="Space Mono" font-size="8" x="586" y="138">SPD: 110kt | RNG: 1.8km | AZ: 052°</text>
</g>
{/*  HOSTILE TARGET BLIP 2 (Quadcopter Swarm x5)  */}
<g className="cursor-pointer" id="blip-tgt02">
{/*  Velocity vector  */}
<line stroke="#FFB4AB" strokeWidth="1.5" x1="260" x2="310" y1="330" y2="300"></line>
{/*  Hostile diamond cluster  */}
<polygon fill="#93000A" points="260,324 266,330 260,336 254,330" stroke="#FFB4AB" strokeWidth="1"></polygon>
<circle cx="253" cy="322" fill="#FFB4AB" r="2.5"></circle>
<circle cx="267" cy="322" fill="#FFB4AB" r="2.5"></circle>
<circle cx="266" cy="338" fill="#FFB4AB" r="2.5"></circle>
{/*  Label  */}
<rect fill="#1F1F23" fillOpacity="0.9" height="28" width="150" x="135" y="340"></rect>
<text fill="#FFB4AB" font-family="Space Mono" font-size="9" font-weight="bold" x="140" y="352">TGT-02: QUAD-SWARM [x5]</text>
<text fill="#E3E2E6" font-family="Space Mono" font-size="8" x="140" y="363">ALT: 180m AGL | RNG: 1.2km</text>
</g>
{/*  HOSTILE TARGET BLIP 3 (High Altitude Recon)  */}
<g className="cursor-pointer" id="blip-tgt03">
<line stroke="#FFDDB8" strokeDasharray="2 2" strokeWidth="1" x1="220" x2="250" y1="110" y2="135"></line>
<polygon fill="#895600" points="220,105 225,110 220,115 215,110" stroke="#FFDDB8" strokeWidth="1"></polygon>
<rect fill="#1F1F23" fillOpacity="0.9" height="26" width="124" x="90" y="92"></rect>
<text fill="#FFDDB8" font-family="Space Mono" font-size="9" font-weight="bold" x="94" y="103">TGT-03: REC-HA [RECON]</text>
<text fill="#E3E2E6" font-family="Space Mono" font-size="8" x="94" y="114">ALT: 4200m | BEARING 310°</text>
</g>
</svg>
{/*  Top-Left Radar HUD Widget: Live Bearing  */}
<div className="absolute top-space-xs left-space-xs bg-surface-container-lowest px-space-sm py-space-xs pointer-events-none">
<span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">PRIMARY BEARING</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container">045.2° TRUE</span>
</div>
{/*  Bottom-Right Radar HUD Widget: Sweep Freq  */}
<div className="absolute bottom-space-xs right-space-xs bg-surface-container-lowest px-space-sm py-space-xs pointer-events-none text-right">
<span className="font-label-sm text-label-sm text-on-surface-variant block uppercase">PRF: 1420 HZ // DOPPLER ON</span>
<span className="font-telemetry-data text-telemetry-data text-secondary-container">TRACKS ACTIVE: 03</span>
</div>
</div>
{/*  Radar Controls Toolbar  */}
<div className="mt-space-sm bg-surface-container-lowest p-space-xs flex flex-wrap items-center justify-between gap-space-xs">
{/*  Range Zoom  */}
<div className="flex items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase px-space-xs">ZOOM:</span>
<button className="px-space-sm py-0.5 bg-surface-container-highest text-primary-container font-label-sm text-label-sm uppercase" type="button">1X [3KM]</button>
<button className="px-space-sm py-0.5 bg-surface-container text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">2X [1.5KM]</button>
<button className="px-space-sm py-0.5 bg-surface-container text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">4X [750M]</button>
</div>
{/*  Layer Toggles  */}
<div className="flex items-center gap-space-xs flex-wrap">
<label className="flex items-center gap-1 bg-surface-container px-space-sm py-0.5 cursor-pointer text-label-sm font-label-sm">
<input checked="" className="accent-primary-container h-3 w-3" type="checkbox"/>
<span className="text-on-surface">THREAT LANES</span>
</label>
<label className="flex items-center gap-1 bg-surface-container px-space-sm py-0.5 cursor-pointer text-label-sm font-label-sm">
<input checked="" className="accent-primary-container h-3 w-3" type="checkbox"/>
<span className="text-on-surface">JAM SECTORS</span>
</label>
<label className="flex items-center gap-1 bg-surface-container px-space-sm py-0.5 cursor-pointer text-label-sm font-label-sm">
<input className="accent-primary-container h-3 w-3" type="checkbox"/>
<span className="text-on-surface-variant">ELEV MESH</span>
</label>
<label className="flex items-center gap-1 bg-surface-container px-space-sm py-0.5 cursor-pointer text-label-sm font-label-sm">
<input checked="" className="accent-primary-container h-3 w-3" type="checkbox"/>
<span className="text-on-surface">AIR CORRIDORS</span>
</label>
</div>
</div>
</div>
{/*  CHRONOLOGICAL TACTICAL FEED & TERMINAL LOG  */}
<div className="bg-surface-container-low p-space-md flex flex-col flex-1">
{/*  Feed Header  */}
<div className="flex items-center justify-between pb-space-xs mb-space-sm bg-surface-container-lowest px-space-sm py-space-xs">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-[16px] text-primary-container">terminal</span>
<span className="font-label-sm text-label-sm text-on-surface font-bold uppercase">LIVE EVENT TELEMETRY STREAM</span>
<span className="w-1.5 h-1.5 bg-primary-container rounded-full animate-pulse"></span>
</div>
{/*  Log Actions & Export  */}
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase flex items-center gap-1" type="button">
<span className="material-symbols-outlined text-[13px]">file_download</span>
<span>EXPORT LOG</span>
</button>
</div>
</div>
{/*  Filter Sub-bar  */}
<div className="flex items-center gap-space-xs mb-space-xs overflow-x-auto pb-space-xs">
<button className="px-space-sm py-space-xs bg-surface-container-highest text-primary-container font-label-sm text-label-sm uppercase font-bold" type="button">ALL EVENTS [6]</button>
<button className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">HOSTILE SPAWNS</button>
<button className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm uppercase" type="button">TRAINEE ACTIONS</button>
<button className="px-space-sm py-space-xs bg-error-container text-error font-label-sm text-label-sm uppercase font-bold flex items-center gap-1" type="button">
<span className="w-1.5 h-1.5 bg-error rounded-full"></span>
<span>CLASSIFICATION ERRORS (1)</span>
</button>
</div>
{/*  Terminal Output Viewport  */}
<div className="bg-surface-container-lowest p-space-sm font-label-sm text-label-sm flex flex-col gap-1.5 overflow-y-auto max-h-56">
<div className="flex items-start gap-space-sm text-on-surface-variant hover:bg-surface-container px-space-xs py-0.5">
<span className="text-secondary-fixed shrink-0 font-telemetry-data text-label-sm">[02:14:10]</span>
<span className="text-on-surface-variant uppercase font-bold shrink-0">SYS:</span>
<span>Target Alpha spawned (Bearing 045°, Range 3.2km, Spd 95kt).</span>
</div>
<div className="flex items-start gap-space-sm text-on-surface-variant hover:bg-surface-container px-space-xs py-0.5">
<span className="text-secondary-fixed shrink-0 font-telemetry-data text-label-sm">[02:16:42]</span>
<span className="text-on-surface-variant uppercase font-bold shrink-0">SYS:</span>
<span>Trainee sensor ping received on Sector 4 surveillance array.</span>
</div>
<div className="flex items-start gap-space-sm text-primary hover:bg-surface-container px-space-xs py-0.5">
<span className="text-secondary-fixed shrink-0 font-telemetry-data text-label-sm">[02:18:05]</span>
<span className="text-primary-container uppercase font-bold shrink-0">TRN:</span>
<span>Radar target lock confirmed on Target Alpha [Track ID #409]. Trainee latency: 3.8s.</span>
</div>
{/*  CRITICAL INCIDENT HIGHLIGHT  */}
<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs bg-surface-container-high px-space-sm py-space-xs">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-error text-[18px]">error</span>
<span className="text-error font-telemetry-data text-label-sm font-bold">[02:20:19]</span>
<div className="flex flex-col">
<span className="text-error font-bold uppercase">TRAINEE FAULT: INCORRECT CLASSIFICATION</span>
<span className="text-on-surface">Target Alpha (FPV Armed) misidentified as Friendly Recon UAV.</span>
</div>
</div>
<button className="self-start sm:self-auto px-space-sm py-space-xs bg-error-container text-error hover:bg-error hover:text-on-error uppercase font-label-sm text-label-sm tracking-wide transition-colors" type="button">
              MARK FOR AAR
            </button>
</div>
<div className="flex items-start gap-space-sm text-on-surface-variant hover:bg-surface-container px-space-xs py-0.5">
<span className="text-secondary-fixed shrink-0 font-telemetry-data text-label-sm">[02:22:50]</span>
<span className="text-on-surface-variant uppercase font-bold shrink-0">SYS:</span>
<span>Swarm Beta inbound bearing 280° - 5 micro-contacts detected via acoustic sensor net.</span>
</div>
<div className="flex items-start gap-space-sm text-primary hover:bg-surface-container px-space-xs py-0.5">
<span className="text-secondary-fixed shrink-0 font-telemetry-data text-label-sm">[02:23:15]</span>
<span className="text-primary-container uppercase font-bold shrink-0">TRN:</span>
<span>RF Jamming Countermeasure CW-1 deployed • 2 contacts disrupted and neutralized.</span>
</div>
</div>
</div>
</div>
{/*  RIGHT COLUMN: TELEMETRY, SCORING & INSTRUCTOR CONTROLS (Cols 16 to 24)  */}
<div className="lg:col-span-9 flex flex-col gap-space-sm">
{/*  TOP RIGHT: LIVE TELEMETRY & EVALUATION SCORING  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-sm">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest px-space-sm py-space-xs">
<span className="font-label-sm text-label-sm text-on-surface font-bold uppercase">EVALUATION METRICS // REAL-TIME</span>
<span className="font-label-sm text-label-sm text-primary-container uppercase">STANDARD SPEC-B</span>
</div>
{/*  3 Quantitative Score Cards  */}
<div className="grid grid-cols-1 sm:grid-cols-3 gap-space-xs">
{/*  Metric 1: Detection Time  */}
<div className="bg-surface-container p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DETECTION TIME</span>
<div className="my-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">4.2s</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm">
<span className="text-on-surface-variant">THRES: &lt;5.0s</span>
<span className="text-primary-container font-bold">NOMINAL</span>
</div>
</div>
{/*  Metric 2: Classification Accuracy  */}
<div className="bg-surface-container p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">CLASS. ACCURACY</span>
<div className="my-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-fixed">85%</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm">
<span className="text-on-surface-variant">17/20 VERIFIED</span>
<span className="text-tertiary-fixed-dim font-bold">CAUTION</span>
</div>
</div>
{/*  Metric 3: Overall Engagement Grade  */}
<div className="bg-surface-container p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EVAL GRADE</span>
<div className="my-space-xs flex items-baseline gap-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-primary">B+</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">/ 842 PTS</span>
</div>
<div className="flex items-center justify-between font-label-sm text-label-sm">
<span className="text-on-surface-variant">TIER: FLIGHT-C</span>
<span className="text-primary-container font-bold">PASSING</span>
</div>
</div>
</div>
{/*  Trainee Biometrics & Stress Monitor Widget  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">ecg_heart</span>
<span className="font-label-sm text-label-sm text-on-surface uppercase font-bold">PHYSIOLOGICAL TELEMETRY [LT. MILLER]</span>
</div>
<span className="px-space-xs bg-surface-container-highest text-tertiary-fixed-dim font-label-sm text-label-sm uppercase font-bold">STRESS: ELEVATED</span>
</div>
<div className="grid grid-cols-2 gap-space-xs mt-space-xs bg-surface-container-lowest p-space-xs">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">HEART RATE</span>
<div className="flex items-baseline gap-1">
<span className="font-telemetry-critical text-telemetry-critical text-on-surface">118</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim">BPM</span>
</div>
</div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">GSR / STRESS COEFFICIENT</span>
<div className="flex items-baseline gap-1">
<span className="font-telemetry-critical text-telemetry-critical text-tertiary-fixed-dim">64%</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">HIGH LOAD</span>
</div>
</div>
</div>
{/*  Biometric Sparkline Chart (SVG)  */}
<div className="w-full h-16 bg-surface-container-lowest relative flex items-end pt-2 px-1">
<svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 300 60">
{/*  Grid threshold line  */}
<line opacity="0.6" stroke="#93000A" strokeDasharray="2 3" strokeWidth="0.75" x1="0" x2="300" y1="20" y2="20"></line>
<text fill="#FFB4AB" font-family="Space Mono" font-size="7" x="5" y="16">INCURSION PEAK • 130 BPM</text>
{/*  Stress Sparkline Path  */}
<path d="M 0 45 L 20 48 L 45 42 L 70 44 L 95 35 L 120 38 L 140 18 L 155 12 L 170 28 L 195 32 L 220 22 L 245 15 L 270 20 L 300 24" fill="none" stroke="#FFB95F" strokeWidth="1.5"></path>
{/*  Gradient fill under path  */}
<polygon fill="#FFB95F" fillOpacity="0.08" points="0,60 0,45 20,48 45,42 70,44 95,35 120,38 140,18 155,12 170,28 195,32 220,22 245,15 270,20 300,24 300,60"></polygon>
{/*  Incursion spike point marker  */}
<circle cx="155" cy="12" fill="#FF3344" r="3"></circle>
<circle cx="245" cy="15" fill="#FF3344" r="3"></circle>
</svg>
</div>
<div className="flex justify-between font-label-sm text-label-sm text-on-surface-variant px-space-xs">
<span>T-10 MIN</span>
<span>T-5 MIN</span>
<span className="text-tertiary-fixed-dim">CURRENT [SPIKE AT 02:22]</span>
</div>
</div>
</div>
{/*  BOTTOM RIGHT: SCENARIO INJECTS & LIVE OVERRIDES  */}
<div className="bg-surface-container-low p-space-md flex flex-col gap-space-sm flex-1">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest px-space-sm py-space-xs">
<span className="font-label-sm text-label-sm text-on-surface font-bold uppercase">INSTRUCTOR OVERRIDES &amp; INJECTS</span>
<span className="font-label-sm text-label-sm text-secondary-container uppercase">TACTICAL GENERATOR</span>
</div>
{/*  Overrides Box  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-sm">
{/*  Visibility / Fog Range Slider  */}
<div className="flex flex-col gap-1">
<div className="flex justify-between items-center text-label-sm font-label-sm">
<span className="text-on-surface-variant uppercase">FOG &amp; ATMOSPHERIC DEGRADATION</span>
<span className="text-secondary-fixed font-telemetry-data text-telemetry-data" id="fog-val">35%</span>
</div>
<input className="w-full h-1 bg-surface-container-highest appearance-none cursor-pointer accent-secondary-container" id="fog-slider" max="100" min="0" type="range" value="35"/>
<div className="flex justify-between text-on-surface-variant font-label-sm text-[8px]">
<span>CLEAR (0%)</span>
<span>MED (50%)</span>
<span>ZERO-VIS (100%)</span>
</div>
</div>
{/*  Environment Multi-Toggles  */}
<div className="grid grid-cols-2 gap-space-xs pt-space-xs">
{/*  Night Mode / NVG  */}
<button className="bg-surface-container-high p-space-xs flex items-center justify-between text-left hover:bg-surface-container-highest transition-colors" id="toggle-nvg" type="button">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface uppercase font-bold">NIGHT / NVG</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">IR SIGNATURES</span>
</div>
<span className="px-space-xs py-0.5 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold uppercase">ACTIVE</span>
</button>
{/*  Jam Radar Injection  */}
<button className="bg-surface-container-high p-space-xs flex items-center justify-between text-left hover:bg-surface-container-highest transition-colors" id="toggle-jamming" type="button">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface uppercase font-bold">RADAR STROBE</span>
<span className="font-label-sm text-label-sm text-error">CH-4 EW JAM</span>
</div>
<span className="px-space-xs py-0.5 bg-error-container text-error font-label-sm text-label-sm font-bold uppercase animate-pulse">JAMMING</span>
</button>
</div>
{/*  Weather & Wind Mini Telemetry  */}
<div className="flex items-center justify-between bg-surface-container-lowest px-space-sm py-space-xs text-label-sm font-label-sm">
<div className="flex items-center gap-1">
<span className="material-symbols-outlined text-[15px] text-secondary-fixed">air</span>
<span className="text-on-surface-variant uppercase">WIND:</span>
<span className="text-on-surface font-telemetry-data text-label-sm">18KT @ 315°</span>
</div>
<div className="flex items-center gap-1">
<span className="material-symbols-outlined text-[15px] text-secondary-fixed">rainy</span>
<span className="text-on-surface-variant uppercase">PRECIP:</span>
<span className="text-on-surface font-telemetry-data text-label-sm">LIGHT DRIZZLE</span>
</div>
</div>
</div>
{/*  Dynamic Threat Injects (High Contrast Tactile Action Buttons)  */}
<div className="flex flex-col gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase font-bold">MANUAL THREAT SPAWNERS</span>
{/*  Spawn Kamikaze FPV  */}
<button className="w-full bg-surface-container p-space-sm flex items-center justify-between text-left hover:bg-error-container hover:text-error transition-all group" id="spawn-kamikaze" type="button">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-error text-[20px]">bolt</span>
<div className="flex flex-col">
<span className="font-label-md text-label-md text-on-surface group-hover:text-error font-bold uppercase">[+] SPAWN FPV KAMIKAZE</span>
<span className="font-label-sm text-label-sm text-on-surface-variant group-hover:text-error">HIGH SPEED DIRECT VECTOR • BEARING 045°</span>
</div>
</div>
<span className="font-label-sm text-label-sm bg-surface-container-highest px-space-xs py-space-xs text-error font-bold">110 KT</span>
</button>
{/*  Spawn Surveillance Drone  */}
<button className="w-full bg-surface-container p-space-sm flex items-center justify-between text-left hover:bg-tertiary-fixed-dim hover:text-on-tertiary-fixed transition-all group" id="spawn-recon" type="button">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-tertiary-fixed-dim text-[20px]">satellite_alt</span>
<div className="flex flex-col">
<span className="font-label-md text-label-md text-on-surface group-hover:text-on-tertiary-fixed font-bold uppercase">[+] SPAWN RECON DRONE</span>
<span className="font-label-sm text-label-sm text-on-surface-variant group-hover:text-on-tertiary-fixed">HIGH-ALTITUDE LOITER • 4,500m AGL</span>
</div>
</div>
<span className="font-label-sm text-label-sm bg-surface-container-highest px-space-xs py-space-xs text-tertiary-fixed-dim font-bold">STEALTH</span>
</button>
{/*  Spawn Full Swarm (CRITICAL ALERT TRIGGER)  */}
<button className="w-full bg-error-container text-error p-space-sm flex items-center justify-between text-left hover:bg-on-error hover:text-error-container transition-all" id="spawn-swarm" type="button">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-[20px] animate-pulse">warning</span>
<div className="flex flex-col">
<span className="font-label-md text-label-md font-bold uppercase tracking-wider">[+] INJECT QUAD-SWARM (x5 CONTACTS)</span>
<span className="font-label-sm text-label-sm opacity-90">MULTIDIRECTIONAL LOW-ALTITUDE SATURATION ATTACK</span>
</div>
</div>
<span className="font-label-sm text-label-sm bg-surface-container-lowest text-error px-space-sm py-space-xs font-bold uppercase">EXECUTE</span>
</button>
</div>
</div>
</div>
</div>
</div>
</main></div>
    </div>
  );
}
