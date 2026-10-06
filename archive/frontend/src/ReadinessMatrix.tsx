import React from 'react';

export default function ReadinessMatrix() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs" data-active-classes="bg-surface-container text-primary-container font-bold border-l-2 border-primary-container"><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="live-instructor-dashboard" href="#"><span>Live Dashboard</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span>Scenario Builder</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="aar-reports" href="#"><span>AAR Reports</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="unit-roster" href="#"><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
{/*  TOP OPERATIONAL CONTROL & BANNER  */}
<section className="w-full bg-surface-container-low px-space-md py-space-sm">
<div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
{/*  Title & Echelon Context  */}
<div className="flex flex-col">
<div className="flex items-center gap-space-sm">
<span className="w-2 h-2 bg-primary-container"></span>
<span className="font-label-sm text-label-sm uppercase text-on-surface-variant tracking-wider">STANAG 4586 LVL-4 AUDIT // TAC-EVAL 24.8</span>
<span className="px-space-xs py-0.5 bg-surface-container-highest text-secondary font-label-sm text-label-sm tracking-widest">[CR-COMPARISON]</span>
</div>
<h1 className="font-headline-md text-headline-md tracking-tight text-primary uppercase mt-0.5">
          Squadron Readiness Matrix <span className="text-on-surface-variant font-headline-sm text-headline-sm">// 104th Tactical UAS Intercept Squadron</span>
</h1>
<p className="font-label-sm text-label-sm text-on-surface-variant uppercase">
          Echelon: Battalion C2 Tactical Command • Flight-Level Differential &amp; Combat Doctrine Certification
        </p>
</div>
{/*  Action & Filter Bar  */}
<div className="flex flex-wrap items-center gap-space-xs">
{/*  Timeframe Segmented Selector  */}
<div className="flex items-center bg-surface-container-lowest p-space-xs">
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">30 DAYS</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm bg-surface-container-highest text-primary-container font-bold" type="button">90 DAYS</button>
<button className="px-space-sm py-1 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface" type="button">ANNUAL</button>
</div>
<button className="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container hover:bg-surface-container-high text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[15px] text-secondary-container">file_download</span>
<span>Defense Audit</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container hover:bg-surface-container-high text-on-surface font-label-sm text-label-sm uppercase transition-colors" type="button">
<span className="material-symbols-outlined text-[15px] text-primary-container">swap_horizontal_circle</span>
<span>Re-Balance Roster</span>
</button>
<button className="flex items-center gap-space-xs px-space-sm py-1 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold uppercase transition-colors shadow-sm" type="button">
<span className="material-symbols-outlined text-[15px]">play_arrow</span>
<span>Simulate Deploy</span>
</button>
</div>
</div>
{/*  Fleet-Wide Global Metrics Strip  */}
<div className="grid grid-cols-2 md:grid-cols-5 gap-space-xs mt-space-sm pt-space-xs">
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Fleet Combat Qual</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">68.0%</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim">[20/28 CR-1]</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-1">
<div className="bg-primary-container h-1 w-[68%]"></div>
</div>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Total Sorties (L90D)</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container">184</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">98.2% COMPL</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-1">
<div className="bg-secondary-container h-1 w-[98%]"></div>
</div>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Kinetic Intercept Rate</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">89.2%</span>
<span className="font-label-sm text-label-sm text-primary-container">+3.4% VS STANAG</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-1">
<div className="bg-primary-container h-1 w-[89%]"></div>
</div>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EW Jamming Efficiency</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container">84.6%</span>
<span className="font-label-sm text-label-sm text-secondary-container font-label-sm">STABLE</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-1">
<div className="bg-secondary-container h-1 w-[84%]"></div>
</div>
</div>
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between col-span-2 md:col-span-1">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Avg Stress Recovery</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-tertiary-fixed-dim">10.8s</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TARGET &lt;10.0s</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-1">
<div className="bg-tertiary-fixed-dim h-1 w-[72%]"></div>
</div>
</div>
</div>
</section>
{/*  3-COLUMN HERO COMPARISON GRID  */}
<section className="p-space-md grid grid-cols-1 lg:grid-cols-3 gap-space-md">
{/*  FLIGHT-A: PHANTOMS  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md">
{/*  Corner Bracket Accents  */}
<div className="absolute top-0 left-0 w-2 h-2 bg-primary-container"></div>
<div className="absolute top-0 right-0 w-2 h-2 bg-primary-container"></div>
<div>
{/*  Card Header  */}
<div className="flex items-start justify-between pb-space-sm bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-primary-container"></span>
<span className="font-label-sm text-label-sm text-primary-container font-bold tracking-wider">UNIT: FLIGHT-A</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">["PHANTOMS"]</span>
</div>
<span className="font-headline-sm text-headline-sm text-primary mt-0.5">Kinetic Air Superiority</span>
</div>
<span className="px-space-sm py-0.5 bg-surface-container-high text-primary-container font-label-sm text-label-sm font-bold uppercase">
            CR-1 FULL
          </span>
</div>
{/*  Commander & Sub-details  */}
<div className="mt-space-sm grid grid-cols-2 gap-space-sm bg-surface-container-lowest p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Flight Lead</span>
<span className="font-label-md text-label-md text-on-surface">Capt. R. Sterling</span>
<span className="font-label-sm text-label-sm text-primary-container">[TRN-7104] CR-1</span>
</div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Pilot Allocation</span>
<span className="font-label-md text-label-md text-on-surface">9 Active Pilots</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">8 CR-1 Full / 1 CR-2</span>
</div>
</div>
{/*  Readiness Score Radial / KPI Banner  */}
<div className="mt-space-sm flex items-center justify-between bg-surface-container p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Readiness Score</span>
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">93.4%</span>
<span className="font-label-sm text-label-sm text-primary uppercase">Combat Mission Ready</span>
</div>
{/*  Inline Mini Visual Meter  */}
<div className="w-16 h-16 flex items-center justify-center relative">
<svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
<path className="text-surface-container-highest" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
<path className="text-primary-container" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="93, 100" strokeLinecap="square" strokeWidth="3"></path>
</svg>
<span className="absolute font-label-sm text-label-sm font-bold text-primary">93%</span>
</div>
</div>
{/*  Telemetry KPIs  */}
<div className="mt-space-sm space-y-space-xs">
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SWARM INTERCEPT RATE</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container">94.2%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SENSOR-TO-SHOOT LATENCY</span>
<span className="font-telemetry-data text-telemetry-data text-primary">1.82s</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SCENARIO SUCCESS RATE</span>
<span className="font-telemetry-data text-telemetry-data text-primary-container">96.0%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>PRIMARY DOCTRINE</span>
<span className="font-label-sm text-label-sm text-on-surface truncate">Kinetic CIWS / Salvo</span>
</div>
</div>
</div>
{/*  Action Footer  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between">
<span className="font-label-sm text-label-sm text-primary-container flex items-center gap-1">
<span className="material-symbols-outlined text-[14px]">verified</span> STANAG CLEARED
        </span>
<button className="px-space-sm py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase" type="button">
          Audit Logs
        </button>
</div>
</div>
{/*  FLIGHT-B: TALONS (WARNING/DEFICIT)  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md">
{/*  Amber/Crimson Alert Bracket  */}
<div className="absolute top-0 left-0 w-2 h-2 bg-error"></div>
<div className="absolute top-0 right-0 w-2 h-2 bg-error"></div>
<div>
{/*  Card Header  */}
<div className="flex items-start justify-between pb-space-sm bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-error animate-pulse"></span>
<span className="font-label-sm text-label-sm text-error font-bold tracking-wider">UNIT: FLIGHT-B</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">["TALONS"]</span>
</div>
<span className="font-headline-sm text-headline-sm text-primary mt-0.5">Swarm &amp; Multi-Axis Defense</span>
</div>
<span className="px-space-sm py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold uppercase">
            DEFICIT / WATCH
          </span>
</div>
{/*  Commander & Sub-details  */}
<div className="mt-space-sm grid grid-cols-2 gap-space-sm bg-surface-container-lowest p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Flight Lead</span>
<span className="font-label-md text-label-md text-on-surface">Lt. J. Miller</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim">[TRN-8842] CR-2 PROV</span>
</div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Pilot Allocation</span>
<span className="font-label-md text-label-md text-on-surface">10 Active Pilots</span>
<span className="font-label-sm text-label-sm text-error font-bold">5 CR-1 / 3 CR-2 / 2 CR-3</span>
</div>
</div>
{/*  Readiness Score Radial / KPI Banner  */}
<div className="mt-space-sm flex items-center justify-between bg-surface-container p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Readiness Score</span>
<span className="font-telemetry-critical text-telemetry-critical text-tertiary-fixed-dim">76.8%</span>
<span className="font-label-sm text-label-sm text-error uppercase">Restricted Escort Only</span>
</div>
<div className="w-16 h-16 flex items-center justify-center relative">
<svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
<path className="text-surface-container-highest" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
<path className="text-tertiary-fixed-dim" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="77, 100" strokeLinecap="square" strokeWidth="3"></path>
</svg>
<span className="absolute font-label-sm text-label-sm font-bold text-tertiary-fixed-dim">77%</span>
</div>
</div>
{/*  Telemetry KPIs  */}
<div className="mt-space-sm space-y-space-xs">
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SWARM INTERCEPT RATE</span>
<span className="font-telemetry-data text-telemetry-data text-tertiary-fixed-dim">84.5%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SENSOR-TO-SHOOT LATENCY</span>
<span className="font-telemetry-data text-telemetry-data text-error">2.34s (+0.52s)</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SCENARIO SUCCESS RATE</span>
<span className="font-telemetry-data text-telemetry-data text-tertiary-fixed-dim">78.0%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>VULNERABILITY DETECTED</span>
<span className="font-label-sm text-label-sm text-error font-bold">IFF Spoof Fail (4 Pilots)</span>
</div>
</div>
</div>
{/*  Action Footer  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between">
<span className="font-label-sm text-label-sm text-error flex items-center gap-1 font-bold">
<span className="material-symbols-outlined text-[14px]">warning</span> REMEDIATION REQ
        </span>
<button className="px-space-sm py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm uppercase font-bold" type="button">
          Recert Track
        </button>
</div>
</div>
{/*  FLIGHT-C: REAPERS (EW/OPERATIONAL)  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md">
{/*  Cyan Corner Bracket  */}
<div className="absolute top-0 left-0 w-2 h-2 bg-secondary-container"></div>
<div className="absolute top-0 right-0 w-2 h-2 bg-secondary-container"></div>
<div>
{/*  Card Header  */}
<div className="flex items-start justify-between pb-space-sm bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-secondary-container"></span>
<span className="font-label-sm text-label-sm text-secondary-container font-bold tracking-wider">UNIT: FLIGHT-C</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">["REAPERS"]</span>
</div>
<span className="font-headline-sm text-headline-sm text-primary mt-0.5">EW &amp; Long-Range Ingress</span>
</div>
<span className="px-space-sm py-0.5 bg-surface-container-high text-secondary-container font-label-sm text-label-sm font-bold uppercase">
            EW CERTIFIED
          </span>
</div>
{/*  Commander & Sub-details  */}
<div className="mt-space-sm grid grid-cols-2 gap-space-sm bg-surface-container-lowest p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Flight Lead</span>
<span className="font-label-md text-label-md text-on-surface">WO1 K. Tarasov</span>
<span className="font-label-sm text-label-sm text-secondary-container">[TRN-8339] CR-1</span>
</div>
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Pilot Allocation</span>
<span className="font-label-md text-label-md text-on-surface">9 Active Pilots</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">7 CR-1 / 2 CR-2</span>
</div>
</div>
{/*  Readiness Score Radial / KPI Banner  */}
<div className="mt-space-sm flex items-center justify-between bg-surface-container p-space-sm">
<div className="flex flex-col">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Readiness Score</span>
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container">88.1%</span>
<span className="font-label-sm text-label-sm text-secondary uppercase">Operational Directed</span>
</div>
<div className="w-16 h-16 flex items-center justify-center relative">
<svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
<path className="text-surface-container-highest" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
<path className="text-secondary-container" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="88, 100" strokeLinecap="square" strokeWidth="3"></path>
</svg>
<span className="absolute font-label-sm text-label-sm font-bold text-secondary-container">88%</span>
</div>
</div>
{/*  Telemetry KPIs  */}
<div className="mt-space-sm space-y-space-xs">
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>EW DISRUPTION EFFICIENCY</span>
<span className="font-telemetry-data text-telemetry-data text-secondary-container">91.8%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SENSOR-TO-SHOOT LATENCY</span>
<span className="font-telemetry-data text-telemetry-data text-primary">2.10s</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>SCENARIO SUCCESS RATE</span>
<span className="font-telemetry-data text-telemetry-data text-secondary-container">89.0%</span>
</div>
<div className="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm bg-surface-container-lowest px-space-sm py-1">
<span>PRIMARY DOCTRINE</span>
<span className="font-label-sm text-label-sm text-on-surface truncate">Directed RF Strobe / Jammer</span>
</div>
</div>
</div>
{/*  Action Footer  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between">
<span className="font-label-sm text-label-sm text-secondary-container flex items-center gap-1 font-bold">
<span className="material-symbols-outlined text-[14px]">shield</span> EW VALIDATED
        </span>
<button className="px-space-sm py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase" type="button">
          EW Matrix
        </button>
</div>
</div>
</section>
{/*  5-PILLAR COMPETENCY RADAR & COMPARATIVE BARS  */}
<section className="px-space-md pb-space-md grid grid-cols-1 lg:grid-cols-12 gap-space-md">
{/*  Left: Five Pillar Comparison Bars (8 Cols)  */}
<div className="lg:col-span-8 bg-surface-container-low p-space-md shadow-md">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-primary-container text-[18px]">equalizer</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold">STANAG 4586 Core Competency Pillars (Differential Analysis)</span>
</div>
<div className="flex items-center gap-space-md font-label-sm text-label-sm">
<span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-primary-container inline-block"></span> Phantoms (A)</span>
<span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-error inline-block"></span> Talons (B)</span>
<span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-secondary-container inline-block"></span> Reapers (C)</span>
</div>
</div>
{/*  Pillar Breakdown Rows  */}
<div className="mt-space-md space-y-space-md">
{/*  Pillar 1  */}
<div className="flex flex-col bg-surface-container-lowest p-space-sm">
<div className="flex items-center justify-between mb-1">
<span className="font-label-sm text-label-sm text-primary uppercase font-bold">1. Threat Detection &amp; Ingress Recognition</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">BENCHMARK: 85%</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-xs text-label-sm font-label-sm">
{/*  Flight A  */}
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-A</span><span className="text-primary-container font-bold">96% [EXCEEDS]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary-container h-1.5 w-[96%]"></div></div>
</div>
{/*  Flight B  */}
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-B</span><span className="text-on-surface">88% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary h-1.5 w-[88%]"></div></div>
</div>
{/*  Flight C  */}
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-C</span><span className="text-secondary-container">92% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-secondary-container h-1.5 w-[92%]"></div></div>
</div>
</div>
</div>
{/*  Pillar 2: IFF Discrimination (CRITICAL DEFICIT IN B)  */}
<div className="flex flex-col bg-surface-container-lowest p-space-sm">
<div className="flex items-center justify-between mb-1">
<div className="flex items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-primary uppercase font-bold">2. IFF Discrimination &amp; Deception Resistance</span>
<span className="px-1 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold">[CRITICAL SQUADRON GAP]</span>
</div>
<span className="font-label-sm text-label-sm text-error font-mono">DELTA: B vs A -27%</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-xs text-label-sm font-label-sm">
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-A</span><span className="text-primary-container font-bold">91% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary-container h-1.5 w-[91%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-error font-bold"><span>FLT-B</span><span>64% [CRITICAL DEFICIT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-error h-1.5 w-[64%] animate-pulse"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-C</span><span className="text-secondary-container">86% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-secondary-container h-1.5 w-[86%]"></div></div>
</div>
</div>
</div>
{/*  Pillar 3: Swarm CIWS Interception  */}
<div className="flex flex-col bg-surface-container-lowest p-space-sm">
<div className="flex items-center justify-between mb-1">
<span className="font-label-sm text-label-sm text-primary uppercase font-bold">3. Swarm Vector &amp; Kinetic CIWS Interception</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">FLT-A LEADS (+9%)</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-xs text-label-sm font-label-sm">
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-A</span><span className="text-primary-container font-bold">95% [EXCEEDS]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary-container h-1.5 w-[95%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-B</span><span className="text-on-surface">86% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary h-1.5 w-[86%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-C</span><span className="text-on-surface-variant">79% [COMPETENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-secondary-container h-1.5 w-[79%]"></div></div>
</div>
</div>
</div>
{/*  Pillar 4: Directed RF & ECM  */}
<div className="flex flex-col bg-surface-container-lowest p-space-sm">
<div className="flex items-center justify-between mb-1">
<span className="font-label-sm text-label-sm text-primary uppercase font-bold">4. Directed RF &amp; Electronic Countermeasures</span>
<span className="font-label-sm text-label-sm text-secondary-container font-mono">FLT-C DOMINANT (+18%)</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-xs text-label-sm font-label-sm">
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-A</span><span className="text-on-surface-variant">78% [COMPETENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary-container h-1.5 w-[78%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-B</span><span className="text-on-surface">82% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary h-1.5 w-[82%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-C</span><span className="text-secondary-container font-bold">96% [EXCEEDS]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-secondary-container h-1.5 w-[96%]"></div></div>
</div>
</div>
</div>
{/*  Pillar 5: Composure & Throttle  */}
<div className="flex flex-col bg-surface-container-lowest p-space-sm">
<div className="flex items-center justify-between mb-1">
<span className="font-label-sm text-label-sm text-primary uppercase font-bold">5. High-Stress Multi-Axis Composure &amp; Salvo Throttle</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-mono">FLT-B WATCH STATUS</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-3 gap-space-xs text-label-sm font-label-sm">
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-A</span><span className="text-primary-container font-bold">90% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-primary-container h-1.5 w-[90%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-tertiary-fixed-dim"><span>FLT-B</span><span>72% [WATCH STATUS]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-tertiary-fixed-dim h-1.5 w-[72%]"></div></div>
</div>
<div className="flex flex-col">
<div className="flex justify-between text-on-surface-variant"><span>FLT-C</span><span className="text-secondary-container">84% [PROFICIENT]</span></div>
<div className="w-full bg-surface-container-highest h-1.5 mt-0.5"><div className="bg-secondary-container h-1.5 w-[84%]"></div></div>
</div>
</div>
</div>
</div>
</div>
{/*  Right: Polygonal Radar Chart Representation & Summary Delta Matrix (4 Cols)  */}
<div className="lg:col-span-4 bg-surface-container-low p-space-md flex flex-col justify-between shadow-md">
<div>
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<span className="font-label-md text-label-md text-primary uppercase font-bold">SQUADRON RADAR GEOMETRY</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">SIM-AXIS</span>
</div>
{/*  Inline SVG Radar Visualization  */}
<div className="w-full flex items-center justify-center p-space-md bg-surface-container-lowest mt-space-sm">
<svg className="w-56 h-56" viewBox="0 0 200 200">
{/*  Background Web Rings  */}
<polygon className="text-surface-container-highest" fill="none" points="100,20 176,55 147,145 53,145 24,55" stroke="currentColor" strokeWidth="1"></polygon>
<polygon className="text-surface-container-highest" fill="none" points="100,50 148,72 130,128 70,128 52,72" stroke="currentColor" strokeWidth="1"></polygon>
<polygon className="text-surface-container-highest" fill="none" points="100,75 124,86 115,114 85,114 76,86" stroke="currentColor" strokeWidth="1"></polygon>
{/*  Axis lines  */}
<line className="text-surface-container-highest" stroke="currentColor" strokeWidth="1" x1="100" x2="100" y1="100" y2="20"></line>
<line className="text-surface-container-highest" stroke="currentColor" strokeWidth="1" x1="100" x2="176" y1="100" y2="55"></line>
<line className="text-surface-container-highest" stroke="currentColor" strokeWidth="1" x1="100" x2="147" y1="100" y2="145"></line>
<line className="text-surface-container-highest" stroke="currentColor" strokeWidth="1" x1="100" x2="53" y1="100" y2="145"></line>
<line className="text-surface-container-highest" stroke="currentColor" strokeWidth="1" x1="100" x2="24" y1="100" y2="55"></line>
{/*  Labels  */}
<text className="fill-current text-on-surface-variant text-[8px] font-mono" text-anchor="middle" x="100" y="14">1. THREAT DET</text>
<text className="fill-current text-on-surface-variant text-[8px] font-mono" text-anchor="start" x="180" y="55">2. IFF</text>
<text className="fill-current text-on-surface-variant text-[8px] font-mono" text-anchor="start" x="150" y="158">3. KINETIC</text>
<text className="fill-current text-on-surface-variant text-[8px] font-mono" text-anchor="end" x="50" y="158">4. RF/EW</text>
<text className="fill-current text-on-surface-variant text-[8px] font-mono" text-anchor="end" x="18" y="55">5. STRESS</text>
{/*  Flight-A Polygon (Green)  */}
<polygon className="text-primary-container" fill="none" points="100,24 169,59 143,141 63,135 32,59" stroke="currentColor" strokeWidth="2"></polygon>
{/*  Flight-C Polygon (Cyan)  */}
<polygon className="text-secondary-container" fill="none" points="100,27 165,61 137,136 55,143 36,62" stroke="currentColor" strokeDasharray="3,2" strokeWidth="1.5"></polygon>
{/*  Flight-B Polygon (Amber/Crimson)  */}
<polygon className="text-error" fill="none" points="100,30 149,71 140,138 60,137 45,67" stroke="currentColor" strokeWidth="1.5"></polygon>
</svg>
</div>
{/*  Delta Highlights Box  */}
<div className="mt-space-sm space-y-space-xs font-label-sm text-label-sm">
<div className="flex items-center justify-between p-space-xs bg-surface-container-lowest">
<span className="text-on-surface-variant">MAX POLAR GAP</span>
<span className="text-error font-bold font-mono">Pillar 2 (IFF): -27%</span>
</div>
<div className="flex items-center justify-between p-space-xs bg-surface-container-lowest">
<span className="text-on-surface-variant">PEAK SYNERGY</span>
<span className="text-primary-container font-mono">Kinetic + EW Interlock</span>
</div>
<div className="flex items-center justify-between p-space-xs bg-surface-container-lowest">
<span className="text-on-surface-variant">RECOMMENDED TACTIC</span>
<span className="text-secondary-container font-mono">A-Lead / C-Support</span>
</div>
</div>
</div>
<div className="mt-space-sm p-space-xs bg-surface-container-highest text-center">
<span className="font-label-sm text-label-sm text-on-surface uppercase tracking-wider">STANAG 4586 PROFILE CONFIRMED</span>
</div>
</div>
</section>
{/*  DETAILED BENCHMARK SCENARIO BREAKDOWN TABLE  */}
<section className="px-space-md pb-space-md">
<div className="bg-surface-container-low p-space-md shadow-md">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-secondary-container text-[18px]">table_rows</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold">Op-Viper Strike: High-Density Swarm Simulation Benchmark Table</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EXERCISE ID: SIM-EX-2025-051</span>
</div>
{/*  Table Container  */}
<div className="overflow-x-auto mt-space-sm">
<table className="w-full text-left font-label-sm text-label-sm">
<thead className="bg-surface-container-highest text-on-surface uppercase font-mono">
<tr>
<th className="p-space-sm">Phase // Metric Scenario</th>
<th className="p-space-sm">Flight-A (Phantoms)</th>
<th className="p-space-sm">Flight-B (Talons)</th>
<th className="p-space-sm">Flight-C (Reapers)</th>
<th className="p-space-sm">Squadron Benchmark</th>
<th className="p-space-sm">Vulnerability Assessment</th>
</tr>
</thead>
<tbody className="divide-y-0">
{/*  Row 1  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container transition-colors">
<td className="p-space-sm">
<div className="flex flex-col">
<span className="font-bold text-on-surface">PH-01: Multi-Directional Ingress</span>
<span className="text-on-surface-variant font-mono">48 Mach 0.8 Low-RCS Drones</span>
</div>
</td>
<td className="p-space-sm font-mono text-primary-container font-bold">
                100% Intercept (48/48)<br/><span className="text-on-surface-variant font-normal">T-Lock: 1.4s</span>
</td>
<td className="p-space-sm font-mono text-on-surface">
                87.5% Intercept (42/48)<br/><span className="text-on-surface-variant font-normal">T-Lock: 2.6s</span>
</td>
<td className="p-space-sm font-mono text-secondary-container">
                93.8% Intercept (45/48)<br/><span className="text-on-surface-variant font-normal">T-Lock: 1.9s</span>
</td>
<td className="p-space-sm font-mono text-on-surface-variant">
                &gt;85.0% Intercept
              </td>
<td className="p-space-sm">
<span className="px-space-xs py-0.5 bg-surface-container-high text-primary-container font-bold uppercase">NOMINAL // SECURE</span>
</td>
</tr>
{/*  Row 2  */}
<tr className="bg-surface-container hover:bg-surface-container-high transition-colors">
<td className="p-space-sm">
<div className="flex flex-col">
<span className="font-bold text-on-surface">PH-02: Mode-4 Spoofing / Decoys</span>
<span className="text-on-surface-variant font-mono">16 Ghost Chirps + 12 Phantoms</span>
</div>
</td>
<td className="p-space-sm font-mono text-on-surface">
                92.8% Correct Lock<br/><span className="text-on-surface-variant font-normal">0 Friendly Fire</span>
</td>
<td className="p-space-sm font-mono text-error font-bold">
                60.7% Correct Lock<br/><span className="text-error font-normal animate-pulse">2 Fratricide Hits Sim</span>
</td>
<td className="p-space-sm font-mono text-secondary-container">
                96.4% Correct Lock<br/><span className="text-on-surface-variant font-normal">Triangulated Strobe</span>
</td>
<td className="p-space-sm font-mono text-on-surface-variant">
                &gt;90.0% Correct Lock
              </td>
<td className="p-space-sm">
<span className="px-space-xs py-0.5 bg-error-container text-on-error-container font-bold uppercase">CRITICAL DEFICIT (FLT-B)</span>
</td>
</tr>
{/*  Row 3  */}
<tr className="bg-surface-container-lowest hover:bg-surface-container transition-colors">
<td className="p-space-sm">
<div className="flex flex-col">
<span className="font-bold text-on-surface">PH-03: Kinetic Swarm Intercept Salvo</span>
<span className="text-on-surface-variant font-mono">Simultaneous 64-Target CIWS</span>
</div>
</td>
<td className="p-space-sm font-mono text-primary-container font-bold">
                96.8% Neutralization<br/><span className="text-on-surface-variant font-normal">Expenditure: 1.2 salvo</span>
</td>
<td className="p-space-sm font-mono text-on-surface">
                82.8% Neutralization<br/><span className="text-on-surface-variant font-normal">Expenditure: 1.8 salvo</span>
</td>
<td className="p-space-sm font-mono text-secondary-container">
                78.1% Neutralization<br/><span className="text-on-surface-variant font-normal">Expenditure: 1.4 salvo</span>
</td>
<td className="p-space-sm font-mono text-on-surface-variant">
                &gt;80.0% Neutralization
              </td>
<td className="p-space-sm">
<span className="px-space-xs py-0.5 bg-surface-container-high text-primary font-bold uppercase">SATISFACTORY (FLT-A PEAK)</span>
</td>
</tr>
{/*  Row 4  */}
<tr className="bg-surface-container hover:bg-surface-container-high transition-colors">
<td className="p-space-sm">
<div className="flex flex-col">
<span className="font-bold text-on-surface">PH-04: High-Power EW Strobe &amp; Jamming</span>
<span className="text-on-surface-variant font-mono">10kW Broadband RF Barrage</span>
</div>
</td>
<td className="p-space-sm font-mono text-on-surface">
                Recovery: 6.8s<br/><span className="text-on-surface-variant font-normal">Telemetry: Degraded</span>
</td>
<td className="p-space-sm font-mono text-tertiary-fixed-dim">
                Recovery: 9.4s<br/><span className="text-on-surface-variant font-normal">Comms Link Loss 12s</span>
</td>
<td className="p-space-sm font-mono text-secondary-container font-bold">
                Recovery: 1.2s<br/><span className="text-secondary font-normal">Active Null Beamforming</span>
</td>
<td className="p-space-sm font-mono text-on-surface-variant">
                Recovery &lt;5.0s
              </td>
<td className="p-space-sm">
<span className="px-space-xs py-0.5 bg-surface-container-high text-secondary-container font-bold uppercase">FLT-C EXCEEDS STANAG</span>
</td>
</tr>
</tbody>
</table>
</div>
</div>
</section>
{/*  SQUADRON RESOURCE ALLOCATION & ACTION DIRECTIVES  */}
<section className="px-space-md pb-space-lg">
<div className="bg-surface-container-low p-space-md shadow-md">
<div className="flex items-center justify-between pb-space-xs bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-primary-container text-[18px]">verified_user</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold">Squadron Directives &amp; Pilot Cross-Deployment Recommendations</span>
</div>
<span className="px-space-xs py-0.5 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold uppercase">
          AUTHORIZATION READY
        </span>
</div>
<div className="grid grid-cols-1 lg:grid-cols-3 gap-space-md mt-space-md">
{/*  Directive 01  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<div className="flex flex-col">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-sm text-label-sm text-secondary-container font-bold uppercase font-mono">DIRECTIVE 01 // CROSS-ATTACH</span>
<span className="w-2 h-2 bg-secondary-container"></span>
</div>
<p className="font-body-sm text-body-sm text-on-surface">
              Cross-attach <strong className="text-secondary font-mono">WO1 Tarasov</strong> (Flight-C EW Lead) to Flight-B during exercise <strong className="text-primary font-mono">SIM-EX-2025-052</strong>. Primary objective: conduct intensive Mode-4 Anti-Spoof remediation to eliminate recurring IFF decoy lock-on deficits.
            </p>
</div>
<div className="mt-space-sm pt-space-xs bg-surface-container-highest flex justify-between items-center px-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">TARGET: +25% IFF ACCURACY</span>
<span className="font-label-sm text-label-sm text-secondary-container font-bold">PRIORITY: HIGH</span>
</div>
</div>
{/*  Directive 02  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<div className="flex flex-col">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-sm text-label-sm text-primary-container font-bold uppercase font-mono">DIRECTIVE 02 // TIER-1 CLEARANCE</span>
<span className="w-2 h-2 bg-primary-container"></span>
</div>
<p className="font-body-sm text-body-sm text-on-surface">
<strong className="text-primary-container font-mono">Flight-A ("Phantoms")</strong> cleared for Tier-1 Unrestricted Kinetic Swarm deployments across all coastal theater sectors. Flight-A's 93.4% readiness satisfies NATO STANAG 4586 Level-4 full-spectrum autonomy directives.
            </p>
</div>
<div className="mt-space-sm pt-space-xs bg-surface-container-highest flex justify-between items-center px-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">STATUS: UNRESTRICTED</span>
<span className="font-label-sm text-label-sm text-primary-container font-bold">CERTIFIED</span>
</div>
</div>
{/*  Directive 03  */}
<div className="bg-surface-container-lowest p-space-sm flex flex-col justify-between">
<div className="flex flex-col">
<div className="flex items-center justify-between mb-space-xs">
<span className="font-label-sm text-label-sm text-error font-bold uppercase font-mono">DIRECTIVE 03 // LOCKOUT RESTRICTION</span>
<span className="w-2 h-2 bg-error"></span>
</div>
<p className="font-body-sm text-body-sm text-on-surface">
<strong className="text-error font-mono">Flight-B ("Talons")</strong> locked from Solo Sector Defense missions until the 4 provisional pilots complete required radar-track anti-deception recertification runs under supervision of Squadron Evaluator.
            </p>
</div>
<div className="mt-space-sm pt-space-xs bg-surface-container-highest flex justify-between items-center px-space-xs">
<span className="font-label-sm text-label-sm text-error font-mono">ACTION: PROVISIONAL HOLD</span>
<span className="font-label-sm text-label-sm text-error font-bold">MANDATORY</span>
</div>
</div>
</div>
{/*  Final Operational Action CTAs  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex flex-col sm:flex-row items-center justify-between gap-space-sm">
<div className="flex items-center gap-space-sm text-on-surface-variant font-label-sm text-label-sm">
<span className="material-symbols-outlined text-[16px] text-primary-container">info</span>
<span>COMMANDER SIGN-OFF: MAJ. VANCE [TAC-01] • EXERCISE EVAL ID: #849-AEGIS</span>
</div>
<div className="flex items-center gap-space-xs w-full sm:w-auto">
<button className="flex-1 sm:flex-none px-space-md py-1.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm font-bold uppercase transition-colors" type="button">
            Print NATO STANAG Report
          </button>
<button className="flex-1 sm:flex-none px-space-md py-1.5 bg-surface-container-high hover:bg-surface-bright text-secondary-container font-label-sm text-label-sm font-bold uppercase transition-colors" type="button">
            Schedule Multi-Flight Sim
          </button>
<button className="flex-1 sm:flex-none px-space-md py-1.5 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold uppercase transition-colors shadow-sm" type="button">
            Apply Re-Allocation
          </button>
</div>
</div>
</div>
</section>
</div></main></div>
    </div>
  );
}
