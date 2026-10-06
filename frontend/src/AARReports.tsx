import React from 'react';

export default function AARReports() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs" data-active-classes="bg-surface-container text-primary-container font-bold border-l-2 border-primary-container"><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="live-instructor-dashboard" href="#"><span className="material-symbols-outlined text-[18px]">grid_view</span><span>Live Dashboard</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span className="material-symbols-outlined text-[18px]">alt_route</span><span>Scenario Builder</span></a><a aria-current="page" className="flex items-center gap-space-md px-space-md py-space-md transition-all uppercase bg-surface-container text-primary-container font-bold border-l-2 border-primary-container" data-path="aar-reports" href="#"><span className="material-symbols-outlined text-[18px]">summarize</span><span>AAR Reports</span></a><a className="flex items-center gap-space-md px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="unit-roster" href="#"><span className="material-symbols-outlined text-[18px]">shield_person</span><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
{/*  PRIMARY OPERATIONAL DEBRIEF STRIP (MISSION METADATA & ACTIONS)  */}
<section className="bg-surface-container-low px-space-md py-space-sm flex flex-col gap-space-sm">
{/*  Top Row: Operational Classification & Mission Header  */}
<div className="flex flex-wrap items-center justify-between gap-space-md">
<div className="flex items-center gap-space-md min-w-0">
<div className="flex items-center gap-space-xs bg-surface-container px-space-sm py-space-xs">
<span className="w-2 h-2 rounded-full bg-primary-container"></span>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">AAR DEBRIEF LOG</span>
</div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-space-sm flex-wrap">
<span className="font-telemetry-critical text-telemetry-critical text-primary tracking-wide">SIM-EX-2025-048</span>
<span className="text-on-surface-variant font-label-md text-label-md">//</span>
<span className="font-headline-sm text-headline-sm text-on-surface tracking-wider uppercase truncate">OP-VIPER STRIKE (PHASE 02 DEBRIEF)</span>
<span className="bg-error-container text-on-error-container px-space-sm py-space-xs font-label-sm text-label-sm uppercase font-bold flex items-center gap-space-xs">
<span className="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
              1 CRITICAL FAULT LOGGED
            </span>
</div>
<div className="flex items-center gap-space-md font-label-sm text-label-sm text-on-surface-variant mt-space-xs flex-wrap">
<span>TRAINEE: <strong className="text-primary font-bold">LT. J. MILLER [TRN-8842]</strong> (CALLSIGN: VANGUARD-3)</span>
<span>•</span>
<span>EVALUATOR: <strong className="text-secondary-fixed-dim font-bold">MAJ. H. VANCE [TAC-01]</strong></span>
<span>•</span>
<span className="font-telemetry-data text-telemetry-data text-on-surface">2025-10-24 14:32:08Z</span>
<span>•</span>
<span>DUR: <strong className="text-on-surface font-telemetry-data text-telemetry-data">18M 00S</strong></span>
<span>•</span>
<span>INTEGRITY: <strong className="text-tertiary-fixed-dim font-telemetry-data text-telemetry-data">74% [MARGINAL]</strong></span>
</div>
</div>
</div>
{/*  Right Composite Scorecard Badge  */}
<div className="flex items-center gap-space-md">
<div className="bg-surface-container-lowest px-space-md py-space-sm flex items-center gap-space-md shadow-sm">
<div className="flex flex-col text-right">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">COMPOSITE SCORE</span>
<div className="flex items-baseline gap-space-xs justify-end">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">82.4</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">/ 100</span>
</div>
</div>
<div className="bg-surface-container px-space-md py-space-xs flex flex-col items-center justify-center">
<span className="font-telemetry-critical text-telemetry-critical text-primary font-bold">B+</span>
<span className="font-label-sm text-label-sm text-primary-fixed-dim uppercase tracking-tighter">QUALIFIED</span>
</div>
</div>
</div>
</div>
{/*  Action Toolbar Row  */}
<div className="flex flex-wrap items-center justify-between gap-space-md pt-space-xs bg-surface-container-lowest px-space-sm py-space-xs">
<div className="flex items-center gap-space-xs flex-wrap">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase px-space-xs">EXERCISE CONTROLS:</span>
<button className="bg-primary-container text-on-primary-container px-space-md py-space-xs font-label-md text-label-md uppercase font-bold flex items-center gap-space-xs hover:bg-primary-fixed transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">picture_as_pdf</span>
<span>EXPORT FULL STANAG AAR</span>
</button>
<button className="bg-surface-container-high text-on-surface hover:bg-surface-bright px-space-md py-space-xs font-label-md text-label-md uppercase flex items-center gap-space-xs transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">dataset</span>
<span>TELEMETRY CSV</span>
</button>
<button className="bg-surface-container text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high px-space-md py-space-xs font-label-md text-label-md uppercase flex items-center gap-space-xs transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">replay</span>
<span>RE-RUN W/ MODIFIERS</span>
</button>
</div>
<div className="flex items-center gap-space-sm">
<span className="font-label-sm text-label-sm text-on-surface-variant">STATION TAC-01 SIGN-OFF:</span>
<button className="bg-primary-fixed-dim text-on-primary-fixed px-space-md py-space-xs font-label-md text-label-md uppercase font-bold flex items-center gap-space-xs hover:bg-primary-container transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">verified</span>
<span>SIGN OFF &amp; ARCHIVE</span>
</button>
</div>
</div>
</section>
{/*  MAIN OPERATIONAL GRID (2-COLUMN HIGH-DENSITY HUD SPLIT)  */}
<div className="grid grid-cols-1 xl:grid-cols-12 gap-space-md p-space-md">
{/*  LEFT COLUMN: SENSOR PLAYBACK RECONSTRUCTION + BIOMETRIC CORRELATOR (7 COLS)  */}
<div className="xl:col-span-7 flex flex-col gap-space-md">
{/*  Panel: 2D Tactical Radar & Vector Reconstruction  */}
<div className="bg-surface-container-low flex flex-col shadow-md">
{/*  Sub-bar Header  */}
<div className="bg-surface-container-lowest px-space-md py-space-xs flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-secondary-container text-[18px]">track_changes</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wider">TACTICAL REPLAY ENGINE // MULTI-SENSOR RECONSTRUCTION</span>
</div>
<div className="flex items-center gap-space-md">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">MGRS: 38TLN 4289 1104</span>
<span className="bg-error-container text-on-error-container px-space-sm py-space-xs font-label-sm text-label-sm uppercase font-bold flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[14px]">warning</span>
              FAULT @ T+02:20.19
            </span>
</div>
</div>
{/*  Radar Canvas Area  */}
<div className="relative bg-surface-container-lowest w-full h-[410px] overflow-hidden flex items-center justify-center select-none">
{/*  Ambient Grid Background Pattern  */}
<div className="absolute inset-0 opacity-15" ></div>
{/*  Radar SVG Overlay  */}
<svg className="w-full h-full absolute inset-0 text-on-surface-variant/40" preserveAspectRatio="xMidYMid meet" viewBox="0 0 640 400">
<defs>
{/*  Jamming Cone Gradient  */}
<radialgradient cx="50%" cy="50%" id="jammingGrad" r="50%">
<stop offset="0%" stopColor="#00e3fd" stopOpacity="0.35"></stop>
<stop offset="100%" stopColor="#00e3fd" stopOpacity="0.0"></stop>
</radialgradient>
{/*  Engagement Sector Gradient  */}
<radialgradient cx="50%" cy="50%" id="ciwsGrad" r="50%">
<stop offset="0%" stopColor="#00ff66" stopOpacity="0.25"></stop>
<stop offset="100%" stopColor="#00ff66" stopOpacity="0.0"></stop>
</radialgradient>
</defs>
{/*  Polar Range Rings (Base DEF-ALPHA is at 320, 200)  */}
<circle cx="320" cy="200" fill="none" r="45" stroke="currentColor" strokeDasharray="2 4" strokeWidth="1"></circle>
<circle cx="320" cy="200" fill="none" r="90" stroke="currentColor" strokeDasharray="3 3" strokeWidth="1"></circle>
<circle cx="320" cy="200" fill="none" r="140" stroke="currentColor" strokeDasharray="4 4" strokeWidth="1"></circle>
<circle cx="320" cy="200" fill="none" r="185" stroke="currentColor" strokeWidth="1"></circle>
{/*  Crosshairs & Azimuth Axes  */}
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="1" x1="320" x2="320" y1="10" y2="390"></line>
<line stroke="currentColor" strokeDasharray="2 4" strokeWidth="1" x1="130" x2="510" y1="200" y2="200"></line>
{/*  Polar Range Distance Indicators  */}
<text fill="#849581" font-family="Space Mono" font-size="9" x="325" y="152">500M</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="325" y="107">1500M</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="325" y="58">2500M</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="325" y="24">3000M MAX</text>
{/*  Compass Bearings  */}
<text fill="#00ff66" font-family="Space Mono" font-size="10" font-weight="bold" x="315" y="16">000° N</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="515" y="204">090° E</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="315" y="396">180° S</text>
<text fill="#849581" font-family="Space Mono" font-size="9" x="80" y="204">270° W</text>
{/*  EW Jamming Sector Arc (Azimuth 020° to 085°, active at T+02:20)  */}
<path d="M 320 200 L 370 60 A 150 150 0 0 1 465 140 Z" fill="url(#jammingGrad)"></path>
<path d="M 370 60 A 150 150 0 0 1 465 140" fill="none" stroke="#00e3fd" strokeDasharray="4 2" strokeWidth="1.5"></path>
<text fill="#00e3fd" font-family="Space Mono" font-size="9" font-weight="bold" x="430" y="85">EW STROBE 35°</text>
{/*  Kinetic CIWS Arc (South-West Flank)  */}
<path d="M 320 200 L 220 280 A 100 100 0 0 1 200 180 Z" fill="url(#ciwsGrad)"></path>
{/*  Vector Flight Paths History Trails  */}
{/*  TGT-01: FPV Kamikaze (Fault Drone #409)  */}
<path d="M 490 50 L 440 110 L 385 145 L 360 170" fill="none" stroke="#ffb4ab" strokeDasharray="2 3" strokeWidth="2"></path>
{/*  TGT-02: Micro-Quad Swarm Ingress (NE Axis)  */}
<path d="M 530 110 L 470 140 L 410 175 L 340 190" fill="none" stroke="#ffb4ab" strokeOpacity="0.8" strokeWidth="1.5"></path>
{/*  TGT-03: Recon Bait / Friendly Decoy Spoof  */}
<path d="M 170 80 L 230 120 L 280 160 L 305 180" fill="none" stroke="#00ff66" strokeDasharray="3 3" strokeWidth="1"></path>
{/*  Target Intercepts / Kills (Green X)  */}
<g transform="translate(410, 175)">
<line stroke="#00ff66" strokeWidth="2" x1="-5" x2="5" y1="-5" y2="5"></line>
<line stroke="#00ff66" strokeWidth="2" x1="5" x2="-5" y1="-5" y2="5"></line>
<circle cx="0" cy="0" fill="none" r="8" stroke="#00ff66" strokeWidth="1"></circle>
<text fill="#00ff66" font-family="Space Mono" font-size="8" x="10" y="4">KILL x5 [EW]</text>
</g>
{/*  Defense Hit / Penetration Flash (Red marker near Base DEF-ALPHA)  */}
<g transform="translate(345, 185)">
<polygon fill="#ffb4ab" points="0,-8 6,6 -6,6" stroke="#93000a" strokeWidth="1"></polygon>
<circle className="animate-pulse" cx="0" cy="0" fill="none" r="12" stroke="#ffb4ab" strokeDasharray="2 2" strokeWidth="1.5"></circle>
<text fill="#ffb4ab" font-family="Space Mono" font-size="8" font-weight="bold" x="10" y="2">SEC-3 HIT [-12% SHLD]</text>
</g>
{/*  Target Node TGT-01 (Current Frozen Position with Fault Marker)  */}
<g transform="translate(360, 170)">
{/*  Threat Ring  */}
<circle cx="0" cy="0" fill="#93000a" fillOpacity="0.3" r="14" stroke="#ffb4ab" strokeWidth="2"></circle>
<circle className="animate-spin" cx="0" cy="0" fill="none" r="22" stroke="#ffb4ab" strokeDasharray="2 2" strokeWidth="1"></circle>
<polygon fill="#ffb4ab" points="0,-6 6,5 -6,5"></polygon>
{/*  Target Tag  */}
<rect fill="#1b1b1f" height="34" stroke="#ffb4ab" strokeWidth="1" width="138" x="18" y="-18"></rect>
<text fill="#ffb4ab" font-family="Space Mono" font-size="9" font-weight="bold" x="24" y="-6">TGT-01 // HOSTILE FPV</text>
<text fill="#ffd7aa" font-family="Space Mono" font-size="8" x="24" y="8">SPOOF MODE-4 (02:20)</text>
<line stroke="#ffb4ab" strokeWidth="1" x1="0" x2="18" y1="0" y2="-8"></line>
</g>
{/*  Trainee Central Base Position: DEF-ALPHA  */}
<g transform="translate(320, 200)">
{/*  Shield Ring  */}
<circle cx="0" cy="0" fill="none" r="20" stroke="#00e3fd" strokeDasharray="6 3" strokeWidth="1.5"></circle>
{/*  Base Marker  */}
<rect fill="#00ff66" fillOpacity="0.2" height="16" stroke="#00ff66" strokeWidth="2" width="16" x="-8" y="-8"></rect>
<rect fill="#00ff66" height="6" width="6" x="-3" y="-3"></rect>
<text fill="#00ff66" font-family="Space Mono" font-size="9" font-weight="bold" x="-32" y="32">DEF-ALPHA [HQ]</text>
<text fill="#849581" font-family="Space Mono" font-size="8" x="-36" y="42">INTEG: 74% / SHLD: 68%</text>
</g>
{/*  Dynamic Replay Sweep Scanner Indicator  */}
<line stroke="#00ff66" strokeOpacity="0.7" strokeWidth="1.5" x1="320" x2="480" y1="200" y2="90"></line>
</svg>
{/*  Top-Left Tactical Overlay Pill  */}
<div className="absolute top-space-sm left-space-sm bg-surface-container/90 px-space-sm py-space-xs font-label-sm text-label-sm text-on-surface-variant flex flex-col gap-space-xs">
<span className="text-primary font-bold">SENSOR RECONSTRUCTION: MULTI-SPECTRAL</span>
<span className="text-secondary-fixed-dim">RF EW: ENGAGED [FREQ 2.4/5.8GHz]</span>
<span className="text-tertiary-fixed-dim">IFF PROTOCOL: MODE-4 (CORRUPTED)</span>
</div>
{/*  Bottom-Right Coordinates Readout  */}
<div className="absolute bottom-space-sm right-space-sm bg-surface-container/90 px-space-sm py-space-xs font-telemetry-data text-telemetry-data text-on-surface-variant">
<span>GRID ZOOM: 1:5000</span> | <span className="text-primary-container">AZM: 052.4°</span>
</div>
</div>
{/*  Interactive Replay Transport Controls  */}
<div className="bg-surface-container px-space-md py-space-sm flex flex-col gap-space-sm">
{/*  Scrubber Bar with Event Markers  */}
<div className="flex flex-col gap-space-xs">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[14px] text-primary-container">history</span>
                EXERCISE PLAYBACK TIMELINE (00:00 - 18:00)
              </span>
<div className="flex items-center gap-space-sm">
<span className="text-error font-bold flex items-center gap-space-xs">
<span className="w-2 h-2 rounded-full bg-error"></span> FAULT INJECT
                </span>
<span className="text-secondary-container">CURRENT: <strong className="font-telemetry-critical text-telemetry-critical text-primary-container">T+02:20.19</strong></span>
</div>
</div>
{/*  Scrubber Track & Markers  */}
<div className="relative w-full h-7 bg-surface-container-lowest flex items-center px-1">
{/*  Threat Intensity Heatmap Bar behind progress  */}
<div className="absolute left-0 top-0 bottom-0 w-full flex opacity-30 pointer-events-none">
<div className="w-[15%] bg-surface-container-highest"></div>
<div className="w-[15%] bg-error-container"></div>
<div className="w-[30%] bg-tertiary-container"></div>
<div className="w-[25%] bg-error-container"></div>
<div className="w-[15%] bg-surface-container-highest"></div>
</div>
{/*  Played Progress Fill  */}
<div className="absolute left-0 top-1 bottom-1 bg-primary-container/20 w-[24%]"></div>
{/*  Timeline Slider Line  */}
<div className="w-full h-1 bg-surface-container-highest relative">
{/*  Playhead  */}
<div className="absolute left-[24%] -top-2.5 w-3 h-6 bg-primary-container flex items-center justify-center cursor-pointer shadow-md">
<div className="w-0.5 h-3 bg-on-primary"></div>
</div>
{/*  Event Markers On Timeline  */}
{/*  T+00:45 Ingress  */}
<div className="absolute left-[8%] -top-1 w-2 h-3 bg-secondary-container" title="T+00:45 Ingress Detected"></div>
{/*  T+02:20 Fault Pin (CRITICAL)  */}
<div className="absolute left-[24%] -top-2 w-3 h-5 bg-error animate-pulse" title="T+02:20 Critical IFF Fault"></div>
{/*  T+04:15 Kinetic Engagement  */}
<div className="absolute left-[45%] -top-1 w-2 h-3 bg-primary-fixed-dim" title="T+04:15 Kinetic Engagement"></div>
{/*  T+06:30 Swarm Intercept  */}
<div className="absolute left-[62%] -top-1 w-2 h-3 bg-primary-container" title="T+06:30 Swarm Intercept"></div>
{/*  T+11:00 Final Wave  */}
<div className="absolute left-[88%] -top-1 w-2 h-3 bg-tertiary-fixed-dim" title="T+11:00 Final Saturation Wave"></div>
</div>
</div>
</div>
{/*  Transport Control Strip  */}
<div className="flex flex-wrap items-center justify-between gap-space-sm pt-space-xs">
<div className="flex items-center gap-space-xs">
<button className="w-8 h-8 bg-surface-container-highest hover:bg-surface-bright flex items-center justify-center text-on-surface" title="Jump Back 10s" type="button">
<span className="material-symbols-outlined text-[18px]">replay_10</span>
</button>
<button className="px-space-md h-8 bg-primary-container text-on-primary-container hover:bg-primary-fixed flex items-center gap-space-xs font-label-md text-label-md uppercase font-bold" title="Toggle Playback" type="button">
<span className="material-symbols-outlined text-[18px]">pause</span>
<span>PAUSE</span>
</button>
<button className="w-8 h-8 bg-surface-container-highest hover:bg-surface-bright flex items-center justify-center text-on-surface" title="Jump Forward 10s" type="button">
<span className="material-symbols-outlined text-[18px]">forward_10</span>
</button>
<div className="h-4 w-px bg-outline-variant mx-space-xs"></div>
{/*  Speed Rate Selectors  */}
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">RATE:</span>
<div className="flex items-center bg-surface-container-lowest">
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">0.25x</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">0.5x</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm bg-primary-container text-on-primary-container font-bold" type="button">1.0x</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">2.0x</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">4.0x</button>
</div>
</div>
{/*  Instant Event Jump Chips  */}
<div className="flex items-center gap-space-xs flex-wrap">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">JUMP:</span>
<button className="px-space-xs py-0.5 bg-surface-container-lowest text-on-surface-variant hover:text-primary font-label-sm text-label-sm" type="button">00:45</button>
<button className="px-space-xs py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold flex items-center gap-space-xs" type="button">
<span>02:20 ★</span>
</button>
<button className="px-space-xs py-0.5 bg-surface-container-lowest text-on-surface-variant hover:text-primary font-label-sm text-label-sm" type="button">04:15</button>
<button className="px-space-xs py-0.5 bg-surface-container-lowest text-on-surface-variant hover:text-primary font-label-sm text-label-sm" type="button">06:30</button>
<button className="px-space-xs py-0.5 bg-surface-container-lowest text-on-surface-variant hover:text-primary font-label-sm text-label-sm" type="button">11:00</button>
</div>
</div>
</div>
</div>
{/*  Panel: Trainee Biometrics, Cognitive Load & Eye-Tracking Telemetry  */}
<div className="bg-surface-container-low flex flex-col shadow-md">
{/*  Sub-bar Header  */}
<div className="bg-surface-container-lowest px-space-md py-space-xs flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-tertiary-fixed-dim text-[18px]">monitor_heart</span>
<span className="font-label-md text-label-md text-on-surface uppercase font-bold tracking-wider">PHYSIOLOGICAL TELEMETRY &amp; COGNITIVE LOAD CORRELATION</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SYNC: TACTICAL REPLAY TIMELINE</span>
</div>
<div className="p-space-md flex flex-col gap-space-md">
{/*  Metric Indicator Cards Row  */}
<div className="grid grid-cols-1 sm:grid-cols-3 gap-space-sm">
<div className="bg-surface-container-lowest p-space-sm flex flex-col">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>HEART RATE (BPM)</span>
<span className="material-symbols-outlined text-[14px] text-error">favorite</span>
</div>
<div className="flex items-baseline gap-space-xs mt-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-error">134</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">BPM PEAK</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">Baseline: 72 BPM (+86% surge)</span>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>COGNITIVE LOAD (GSR)</span>
<span className="material-symbols-outlined text-[14px] text-tertiary-fixed-dim">psychology</span>
</div>
<div className="flex items-baseline gap-space-xs mt-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-tertiary-fixed-dim">89%</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-bold">[SATURATION]</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">Threshold Exceeded: 4m 12s</span>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>EYE TUNNELING INDEX</span>
<span className="material-symbols-outlined text-[14px] text-secondary-container">visibility</span>
</div>
<div className="flex items-baseline gap-space-xs mt-space-xs">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container">68%</span>
<span className="font-label-sm text-label-sm text-error font-bold">[CRITICAL TUNNEL]</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant mt-1">Fixation on TGT-03 Decoy: 9.4s</span>
</div>
</div>
{/*  Synchronized SVG Waveform Chart (HR BPM & GSR Load Curves)  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span className="flex items-center gap-space-sm">
<span className="flex items-center gap-space-xs text-error font-bold">
<span className="w-2 h-0.5 bg-error inline-block"></span> HEART RATE
                </span>
<span className="flex items-center gap-space-xs text-secondary-container font-bold">
<span className="w-2 h-0.5 bg-secondary-container inline-block"></span> COGNITIVE SATURATION INDEX
                </span>
</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">SPIKE CORRELATES TO T+02:20 IFF FAULT</span>
</div>
{/*  Waveform SVG Container  */}
<div className="relative w-full h-28 overflow-hidden">
<svg className="w-full h-full text-outline-variant/30" preserveAspectRatio="none" viewBox="0 0 600 100">
{/*  Background Gridlines  */}
<line stroke="currentColor" strokeDasharray="2 4" x1="0" x2="600" y1="25" y2="25"></line>
<line stroke="currentColor" strokeDasharray="2 4" x1="0" x2="600" y1="50" y2="50"></line>
<line stroke="currentColor" strokeDasharray="2 4" x1="0" x2="600" y1="75" y2="75"></line>
{/*  Critical Event Vertical Reference Marker at T+02:20 (X = 144)  */}
<line stroke="#ffb4ab" strokeDasharray="2 2" strokeWidth="1.5" x1="144" x2="144" y1="0" y2="100"></line>
{/*  Trainee GSR / Cognitive Saturation Curve (Muted Cyan)  */}
<path d="M 0 82 Q 40 80 80 75 T 130 50 L 144 20 L 170 30 Q 220 40 300 48 T 420 52 L 480 32 L 540 60 L 600 78" fill="none" stroke="#00e3fd" strokeWidth="1.5"></path>
{/*  Heart Rate Waveform Curve (Threat Red)  */}
<path d="M 0 75 Q 30 74 70 70 T 120 58 L 144 12 L 180 25 Q 240 38 320 50 T 430 60 L 490 28 L 540 55 L 600 68" fill="none" stroke="#ffb4ab" strokeWidth="2"></path>
{/*  Spike Focus Anchor  */}
<circle className="animate-pulse" cx="144" cy="12" fill="#ffb4ab" r="3.5"></circle>
</svg>
{/*  Annotation callout directly pinned over chart  */}
<div className="absolute left-[24%] top-1 bg-error-container text-on-error-container px-space-xs py-0.5 font-label-sm text-label-sm font-bold flex items-center gap-space-xs">
<span>! FAULT OCCURRED (HR: 134 / COG: 89%)</span>
</div>
</div>
{/*  Eye-Tracking Diagnostics Summary Bar  */}
<div className="bg-surface-container p-space-sm flex items-center justify-between text-on-surface font-body-sm text-body-sm">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">center_focus_strong</span>
<span><strong>SACCADIC GAZE DEFICIT:</strong> Fixation lock on decoy target #03 blinded trainee to 4x flanking FPV incursions on East Sector.</span>
</div>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-bold uppercase whitespace-nowrap">SEVERITY: HIGH</span>
</div>
</div>
</div>
</div>
</div>
{/*  RIGHT COLUMN: EVALUATION RUBRIC, CHRONOLOGY & DEBRIEF NOTES (5 COLS)  */}
<div className="xl:col-span-5 flex flex-col gap-space-md">
{/*  Panel: Evaluation Breakdown & Competency Rubric Matrix  */}
<div className="bg-surface-container-low flex flex-col shadow-md">
{/*  Sub-bar Header  */}
<div className="bg-surface-container-lowest px-space-md py-space-xs flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-primary-container text-[18px]">fact_check</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wider">EVALUATION BREAKDOWN &amp; RUBRIC MATRIX</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SPEC: C2-EVAL-v4.8</span>
</div>
<div className="p-space-md flex flex-col gap-space-md">
{/*  Competency Progress Bars  */}
<div className="flex flex-col gap-space-sm">
{/*  Metric 1: Threat Detection & Ingress Recognition  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center font-label-sm text-label-sm">
<span className="text-on-surface font-bold">1. THREAT DETECTION &amp; INGRESS RECOGNITION</span>
<span className="text-primary-container font-telemetry-data text-telemetry-data">94% [EXCEEDS SPEC]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative">
<div className="bg-primary-container h-full w-[94%]"></div>
{/*  Benchmark line at 80%  */}
<div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-outline" title="Standard Target: 80%"></div>
</div>
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>Avg Detection Latency: 2.1s (Standard: 3.5s)</span>
<span className="text-primary-fixed-dim">+14% OVER SPEC</span>
</div>
</div>
{/*  Metric 2: Classification & IFF Discrimination (CRITICAL DEFICIT)  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center font-label-sm text-label-sm">
<span className="text-on-surface font-bold">2. CLASSIFICATION &amp; IFF DISCRIMINATION</span>
<span className="text-error font-telemetry-data text-telemetry-data">68% [NEEDS IMPROVEMENT]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative">
<div className="bg-error h-full w-[68%]"></div>
<div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-outline"></div>
</div>
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>1 Critical Misclassification on Mode-4 Spoof Drone</span>
<span className="text-error">-12% BELOW SPEC</span>
</div>
</div>
{/*  Metric 3: Weapon Allocation & Jamming Efficacy  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center font-label-sm text-label-sm">
<span className="text-on-surface font-bold">3. ENGAGEMENT PRIORITIZATION &amp; WEAPON ALLOCATION</span>
<span className="text-secondary-fixed-dim font-telemetry-data text-telemetry-data">84% [PROFICIENT]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative">
<div className="bg-secondary-fixed-dim h-full w-[84%]"></div>
<div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-outline"></div>
</div>
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>RF Jammer deployment optimal; minor kinetic CIWS lag</span>
<span className="text-primary-fixed-dim">+4% OVER SPEC</span>
</div>
</div>
{/*  Metric 4: Swarm Countermeasure Efficacy  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center font-label-sm text-label-sm">
<span className="text-on-surface font-bold">4. SWARM COUNTERMEASURE EFFICACY</span>
<span className="text-primary-container font-telemetry-data text-telemetry-data">88% [PROFICIENT]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative">
<div className="bg-primary-container h-full w-[88%]"></div>
<div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-outline"></div>
</div>
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>Neutralized: 34 / 38 Drones (4 kinetic leaks logged)</span>
<span className="text-primary-fixed-dim">PASS [SPEC &gt;85%]</span>
</div>
</div>
{/*  Metric 5: Situational Composure & Recovery  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center font-label-sm text-label-sm">
<span className="text-on-surface font-bold">5. SITUATIONAL COMPOSURE &amp; STRESS RECOVERY</span>
<span className="text-tertiary-fixed-dim font-telemetry-data text-telemetry-data">78% [COMPETENT]</span>
</div>
<div className="w-full bg-surface-container-highest h-2 relative">
<div className="bg-tertiary-fixed-dim h-full w-[78%]"></div>
<div className="absolute top-0 bottom-0 left-[80%] w-0.5 bg-outline"></div>
</div>
<div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm">
<span>Post-fault stabilization time: 12.4s (Target: &lt;15s)</span>
<span className="text-on-surface-variant">NOMINAL RANGE</span>
</div>
</div>
</div>
</div>
</div>
{/*  Panel: Key Event Chronology & Instructor Debrief Notes  */}
<div className="bg-surface-container-low flex flex-col shadow-md">
{/*  Sub-bar Header with Timeline Filter Buttons  */}
<div className="bg-surface-container-lowest px-space-md py-space-xs flex items-center justify-between">
<div className="flex items-center gap-space-sm">
<span className="material-symbols-outlined text-secondary-container text-[18px]">history_edu</span>
<span className="font-label-md text-label-md text-on-surface uppercase font-bold tracking-wider">EVENT CHRONOLOGY &amp; INSTRUCTOR BOOKMARKS</span>
</div>
<div className="flex items-center gap-space-xs">
<button className="bg-surface-container px-space-xs py-0.5 font-label-sm text-label-sm text-primary font-bold" type="button">ALL (5)</button>
<button className="hover:bg-surface-container px-space-xs py-0.5 font-label-sm text-label-sm text-on-surface-variant" type="button">FAULTS (1)</button>
<button className="hover:bg-surface-container px-space-xs py-0.5 font-label-sm text-label-sm text-on-surface-variant" type="button">KILLS (2)</button>
</div>
</div>
<div className="p-space-md flex flex-col gap-space-md">
{/*  Chronology Feed List  */}
<div className="flex flex-col gap-space-xs max-h-56 overflow-y-auto">
{/*  Item 1: Early Warning  */}
<div className="p-space-sm bg-surface-container-lowest flex items-start justify-between gap-space-sm">
<div className="flex items-start gap-space-sm">
<span className="font-telemetry-data text-telemetry-data text-secondary-container whitespace-nowrap">00:32</span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-primary font-bold uppercase">EVENT // EARLY INGRESS CONTACT</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Radar early warning acquisition TGT-01 ingress bearing 045° (Range 2800m).</span>
</div>
</div>
<span className="font-telemetry-data text-telemetry-data text-primary-container whitespace-nowrap">+10 PTS</span>
</div>
{/*  Item 2: Critical Fault  */}
<div className="p-space-sm bg-error-container/20 flex items-start justify-between gap-space-sm">
<div className="flex items-start gap-space-sm">
<span className="font-telemetry-data text-telemetry-data text-error whitespace-nowrap font-bold">02:20</span>
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="bg-error text-on-error px-space-xs py-0.2 font-label-sm text-label-sm uppercase font-bold">FAULT (CRITICAL)</span>
<span className="font-label-sm text-label-sm text-error font-bold uppercase">IFF MISIDENTIFICATION</span>
</div>
<span className="font-body-sm text-body-sm text-on-error-container mt-0.5">Trainee classified Hostile FPV Drone #409 as Friendly Recon due to spoofed Mode-4 transponder. Reaction delay: +4.8s.</span>
</div>
</div>
<span className="font-telemetry-data text-telemetry-data text-error whitespace-nowrap font-bold">-25 PTS</span>
</div>
{/*  Item 3: Inject Recovery  */}
<div className="p-space-sm bg-surface-container-lowest flex items-start justify-between gap-space-sm">
<div className="flex items-start gap-space-sm">
<span className="font-telemetry-data text-telemetry-data text-secondary-container whitespace-nowrap">02:35</span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-secondary-fixed-dim font-bold uppercase">RECOVERY // EW OVERRIDE</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Trainee cross-checked thermal optical payload, detected absence of friendly IR flash, and released wideband RF Strobe.</span>
</div>
</div>
<span className="font-telemetry-data text-telemetry-data text-primary-container whitespace-nowrap">+15 PTS</span>
</div>
{/*  Item 4: Kinetic Intercept  */}
<div className="p-space-sm bg-surface-container-lowest flex items-start justify-between gap-space-sm">
<div className="flex items-start gap-space-sm">
<span className="font-telemetry-data text-telemetry-data text-secondary-container whitespace-nowrap">04:12</span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-primary-container font-bold uppercase">KILL CONFIRMED // EW DIRECTED STROBE</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">5x Micro-Quad contacts neutralized via Directed RF Jammer cone.</span>
</div>
</div>
<span className="font-telemetry-data text-telemetry-data text-primary-container whitespace-nowrap">+20 PTS</span>
</div>
{/*  Item 5: Base Hit Damage  */}
<div className="p-space-sm bg-surface-container-lowest flex items-start justify-between gap-space-sm">
<div className="flex items-start gap-space-sm">
<span className="font-telemetry-data text-telemetry-data text-tertiary-fixed-dim whitespace-nowrap">07:45</span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-bold uppercase">DAMAGE // PERIMETER LEAK</span>
<span className="font-body-sm text-body-sm text-on-surface-variant">Kinetic penetrator proximity airburst; Sector 3 kinetic shield integrity degraded by 22%.</span>
</div>
</div>
<span className="font-telemetry-data text-telemetry-data text-error whitespace-nowrap">-12 PTS</span>
</div>
</div>
{/*  Debrief Notes & Voice Memo Assessment Block  */}
<div className="bg-surface-container p-space-sm flex flex-col gap-space-xs">
<div className="flex justify-between items-center">
<span className="font-label-sm text-label-sm text-on-surface uppercase font-bold flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-primary">rate_review</span>
                EVALUATOR DEBRIEF NOTES // MAJ. H. VANCE
              </span>
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 rounded-full bg-secondary-container"></span>
<span className="font-label-sm text-label-sm text-secondary-container uppercase">VOICE MEMO LOGGED [01:42]</span>
</div>
</div>
{/*  Preset Tactical Debrief Tags  */}
<div className="flex flex-wrap gap-space-xs my-space-xs">
<span className="bg-error-container text-on-error-container px-space-xs py-0.5 font-label-sm text-label-sm uppercase font-bold">#TUNNEL_VISION_WARNING</span>
<span className="bg-surface-container-highest text-on-surface-variant px-space-xs py-0.5 font-label-sm text-label-sm uppercase">#IFF_VERIFICATION_CHECKLIST</span>
<span className="bg-primary-container/20 text-primary-container px-space-xs py-0.5 font-label-sm text-label-sm uppercase font-bold">#EXCELLENT_EW_DISCIPLINE</span>
</div>
{/*  Evaluator Written Assessment Field  */}
<div className="bg-surface-container-lowest p-space-sm text-on-surface font-body-sm text-body-sm leading-relaxed">
              "LT. Miller exhibited rapid initial ingress detection and exceptional RF EW strobe accuracy. However, target fixation on the low-threat decoy bait (#TGT-03) caused severe situational blindness at T+02:20, permitting an adversary spoofed beacon to infiltrate the inner perimeter. Trainee regained composure rapidly after instructor override."
            </div>
{/*  Recommendation & Next Steps Directive  */}
<div className="p-space-sm bg-surface-container-highest flex items-start gap-space-sm">
<span className="material-symbols-outlined text-tertiary-fixed-dim text-[18px]">assignment_turned_in</span>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim uppercase font-bold">DIRECTIVE / REMEDIATION ORDER:</span>
<span className="font-body-sm text-body-sm text-on-surface">Assign LT. Miller to <strong className="text-primary font-bold">SIM-EX-2025-052 (Advanced Spoofed Beacon Discrimination &amp; Saccade Discipline)</strong> prior to live-fire battery qualification.</span>
</div>
</div>
{/*  Official Signatures Block  */}
<div className="pt-space-xs grid grid-cols-2 gap-space-sm">
<div className="bg-surface-container-lowest p-space-xs flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EVALUATOR SIGNATURE:</span>
<div className="flex items-center gap-space-xs text-primary font-label-sm text-label-sm mt-0.5">
<span className="material-symbols-outlined text-[14px]">check_circle</span>
<span>MAJ. H. VANCE // VERIFIED</span>
</div>
</div>
<div className="bg-surface-container-lowest p-space-xs flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">TRAINEE ACKNOWLEDGMENT:</span>
<div className="flex items-center gap-space-xs text-secondary-container font-label-sm text-label-sm mt-0.5">
<span className="material-symbols-outlined text-[14px]">draw</span>
<span>LT. J. MILLER // SIGNED 14:38Z</span>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
</div></main></div>
    </div>
  );
}
