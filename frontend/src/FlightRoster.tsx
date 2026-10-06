import React from 'react';

export default function FlightRoster() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs"><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="live-instructor-dashboard" href="#"><span>Live Dashboard</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span>Scenario Builder</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="aar-reports" href="#"><span>AAR Reports</span></a><a className="flex items-center px-space-md py-space-md bg-surface-container text-primary-container font-bold border-l-2 border-primary-container font-label-md text-label-md uppercase" data-path="unit-roster" href="#roster-section"><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
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
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md border border-transparent hover:border-primary-container/40 transition-colors">
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
{/*  Interactive Pilot Allocation  */}
<button className="flex flex-col text-left group p-1 -m-1 hover:bg-surface-container transition-colors border border-dashed border-outline-variant hover:border-primary-container" onclick="selectFlightFilter('flight-a')" title="Click to inspect Flight-A Pilots" type="button">
<div className="flex items-center justify-between w-full">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase group-hover:text-primary-container">Pilot Allocation</span>
<span className="material-symbols-outlined text-[13px] text-primary-container">open_in_new</span>
</div>
<span className="font-label-md text-label-md text-primary font-bold">9 Active Pilots</span>
<span className="font-label-sm text-label-sm text-primary-container">8 CR-1 Full / 1 CR-2</span>
</button>
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
{/*  Action Footer with Interactive Trigger  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-primary-container flex items-center gap-1">
<span className="material-symbols-outlined text-[14px]">verified</span> STANAG CLEARED
        </span>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-0.5 bg-primary-container/20 border border-primary-container/60 hover:bg-primary-container hover:text-on-primary text-primary-container font-label-sm text-label-sm uppercase font-bold transition-all flex items-center gap-1" onclick="selectFlightFilter('flight-a')" type="button">
<span className="material-symbols-outlined text-[12px]">group</span>
<span>Roster [9]</span>
</button>
<button className="px-space-sm py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase" type="button">
            Audit Logs
          </button>
</div>
</div>
</div>
{/*  FLIGHT-B: TALONS (WARNING/DEFICIT)  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md border border-transparent hover:border-error/40 transition-colors">
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
{/*  Interactive Pilot Allocation  */}
<button className="flex flex-col text-left group p-1 -m-1 hover:bg-surface-container transition-colors border border-dashed border-outline-variant hover:border-error" onclick="selectFlightFilter('flight-b')" title="Click to inspect Flight-B Pilots" type="button">
<div className="flex items-center justify-between w-full">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase group-hover:text-error">Pilot Allocation</span>
<span className="material-symbols-outlined text-[13px] text-error">open_in_new</span>
</div>
<span className="font-label-md text-label-md text-on-surface font-bold">10 Active Pilots</span>
<span className="font-label-sm text-label-sm text-error font-bold">5 CR-1 / 3 CR-2 / 2 CR-3</span>
</button>
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
{/*  Action Footer with Interactive Trigger  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-error flex items-center gap-1 font-bold">
<span className="material-symbols-outlined text-[14px]">warning</span> REMEDIATION REQ
        </span>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-0.5 bg-error-container text-on-error-container border border-error/60 hover:bg-error hover:text-surface font-label-sm text-label-sm uppercase font-bold transition-all flex items-center gap-1" onclick="selectFlightFilter('flight-b')" type="button">
<span className="material-symbols-outlined text-[12px]">group</span>
<span>Roster [10]</span>
</button>
<button className="px-space-sm py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase" type="button">
            Recert Track
          </button>
</div>
</div>
</div>
{/*  FLIGHT-C: REAPERS (EW/OPERATIONAL)  */}
<div className="bg-surface-container-low p-space-md relative flex flex-col justify-between shadow-md border border-transparent hover:border-secondary-container/40 transition-colors">
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
{/*  Interactive Pilot Allocation  */}
<button className="flex flex-col text-left group p-1 -m-1 hover:bg-surface-container transition-colors border border-dashed border-outline-variant hover:border-secondary-container" onclick="selectFlightFilter('flight-c')" title="Click to inspect Flight-C Pilots" type="button">
<div className="flex items-center justify-between w-full">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase group-hover:text-secondary-container">Pilot Allocation</span>
<span className="material-symbols-outlined text-[13px] text-secondary-container">open_in_new</span>
</div>
<span className="font-label-md text-label-md text-secondary-container font-bold">9 Active Pilots</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">7 CR-1 / 2 CR-2</span>
</button>
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
{/*  Action Footer with Interactive Trigger  */}
<div className="mt-space-md pt-space-sm bg-surface-container-lowest -mx-space-md -mb-space-md p-space-sm px-space-md flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-secondary-container flex items-center gap-1 font-bold">
<span className="material-symbols-outlined text-[14px]">shield</span> EW VALIDATED
        </span>
<div className="flex items-center gap-space-xs">
<button className="px-space-sm py-0.5 bg-secondary-container/20 border border-secondary-container/60 hover:bg-secondary-container hover:text-on-secondary text-secondary-container font-label-sm text-label-sm uppercase font-bold transition-all flex items-center gap-1" onclick="selectFlightFilter('flight-c')" type="button">
<span className="material-symbols-outlined text-[12px]">group</span>
<span>Roster [9]</span>
</button>
<button className="px-space-sm py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase" type="button">
          EW Matrix
        </button>
</div>
</div>
</div>
</section>
{/*  INTERACTIVE FLIGHT PILOT INSPECTION & QUALIFICATION ROSTER  */}
<section className="px-space-md pb-space-md" id="roster-section">
<div className="bg-surface-container-low p-space-md shadow-md border-t-2 border-primary-container">
{/*  Header & Global Roster Controls  */}
<div className="flex flex-col lg:flex-row lg:items-center justify-between pb-space-xs bg-surface-container-lowest -mx-space-md -mt-space-md p-space-sm px-space-md gap-space-sm">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-primary-container text-[20px]">badge</span>
<div className="flex flex-col">
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wider">Flight Pilot Inspection &amp; Qualification Roster</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">PERSONNEL READINESS AUDIT // STANAG 4586 LEVEL-4 OPERATOR CERT</span>
</div>
</div>
<div className="flex items-center gap-space-sm">
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono uppercase" id="roster-showing-count">SHOWING 28 / 28 PILOTS</span>
<button className="px-space-sm py-1 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase flex items-center gap-1" onclick="resetFilters()" type="button">
<span className="material-symbols-outlined text-[13px]">refresh</span>
<span>Reset Filters</span>
</button>
</div>
</div>
{/*  Flight Pills + Status Filters + Live Summary Telemetry Box  */}
<div className="mt-space-md flex flex-col xl:flex-row items-stretch xl:items-center justify-between gap-space-md bg-surface-container-lowest p-space-sm border border-outline-variant">
{/*  Flight Filter Tabs  */}
<div className="flex flex-wrap items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono uppercase pr-1">FLIGHT:</span>
<button className="flight-pill px-space-sm py-1 font-label-sm text-label-sm border border-primary-container bg-primary-container text-on-primary font-bold transition-all" data-flight="all" onclick="selectFlightFilter('all')" type="button">
  ALL SQUADRON (28)
</button>
<button className="flight-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-primary-container transition-all" data-flight="flight-a" onclick="selectFlightFilter('flight-a')" type="button">
  FLIGHT-A 'PHANTOMS' (9)
</button>
<button className="flight-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-error transition-all" data-flight="flight-b" onclick="selectFlightFilter('flight-b')" type="button">
  FLIGHT-B 'TALONS' (10)
</button>
<button className="flight-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-secondary-container transition-all" data-flight="flight-c" onclick="selectFlightFilter('flight-c')" type="button">
  FLIGHT-C 'REAPERS' (9)
</button>
</div>
{/*  Status Filters  */}
<div className="flex flex-wrap items-center gap-space-xs">
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono uppercase pr-1">RATING:</span>
<button className="status-pill px-space-sm py-1 font-label-sm text-label-sm border border-primary-container bg-surface-container-high text-primary-container font-bold transition-all" data-status="all" onclick="selectStatusFilter('all')" type="button">
  ALL STATUS
</button>
<button className="status-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-primary-container transition-all" data-status="CR-1" onclick="selectStatusFilter('CR-1')" type="button">
  CR-1 FULL
</button>
<button className="status-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-tertiary-fixed-dim transition-all" data-status="CR-2" onclick="selectStatusFilter('CR-2')" type="button">
  CR-2 PROV
</button>
<button className="status-pill px-space-sm py-1 font-label-sm text-label-sm border border-outline-variant bg-surface-container text-on-surface hover:border-error transition-all" data-status="CR-3" onclick="selectStatusFilter('CR-3')" type="button">
  CR-3 DEFICIT
</button>
</div>
</div>
{/*  Active Flight Dynamic Telemetry Strip  */}
<div className="mt-space-sm grid grid-cols-2 md:grid-cols-4 gap-space-xs" id="roster-telemetry-strip">
<div className="bg-surface-container p-space-sm flex flex-col justify-between border-l-2 border-primary-container">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Echelon Sub-Group</span>
<span className="font-label-md text-label-md text-primary font-bold mt-1" id="telem-flight-name">ALL SQUADRON (104th)</span>
<span className="font-label-sm text-label-sm text-on-surface-variant" id="telem-flight-echelon">STANAG Profile: Joint Ops</span>
</div>
<div className="bg-surface-container p-space-sm flex flex-col justify-between border-l-2 border-secondary-container">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Avg Reaction Latency</span>
<div className="flex items-baseline gap-space-xs mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container" id="telem-avg-latency">2.08s</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">NOMINAL</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant" id="telem-latency-delta">Within 2.50s standard</span>
</div>
<div className="bg-surface-container p-space-sm flex flex-col justify-between border-l-2 border-primary-container">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">IFF Discrimination Qual</span>
<div className="flex items-baseline gap-space-xs mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container" id="telem-iff-rate">81.4%</span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim" id="telem-iff-status">22/28 CERT</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant" id="telem-iff-benchmark">Benchmark &gt;80%</span>
</div>
<div className="bg-surface-container p-space-sm flex flex-col justify-between border-l-2 border-error">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">Deficit / Watch Flag</span>
<div className="flex items-baseline gap-space-xs mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-error" id="telem-deficit-count">2 CR-3 / 6 CR-2</span>
<span className="font-label-sm text-label-sm text-error font-bold" id="telem-recert-badge">RECERT REQ</span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant" id="telem-deficit-desc">IFF Spoof Remediation Track</span>
</div>
</div>
{/*  Pilots Grid Cards  */}
<div className="mt-space-md grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-space-sm" id="pilot-cards-container">
{/*  PILOT 1 (Flight A Lead)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-primary-container transition-all flex flex-col justify-between" data-flight="flight-a" data-name="Sterling" data-status="CR-1">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-primary-container"></span>
<span className="font-label-sm text-label-sm text-primary-container font-mono font-bold">FLIGHT-A // LEAD</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-7104]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">Capt. R. Sterling</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "AEGIS-01"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-primary-container/40 text-primary-container font-label-sm text-label-sm font-bold font-mono">CR-1 FULL</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-primary font-bold">Kinetic Swarm CIWS / Salvo Lead</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">24</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-primary-container font-bold">98.2%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-primary-container font-bold">96%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-primary font-bold">1.54s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-primary-container flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">verified</span> COMBAT MISSION READY
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Capt. R. Sterling (AEGIS-01) - Cleared Tier-1 Operations.')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-primary-container hover:text-on-primary text-secondary font-label-sm text-label-sm uppercase font-mono" onclick="alert('Re-Test not required. Pilot holds current CR-1 rating.')" type="button">Audit</button>
</div>
</div>
</div>
{/*  PILOT 2 (Flight A)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-primary-container transition-all flex flex-col justify-between" data-flight="flight-a" data-name="Chen" data-status="CR-1">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-primary-container"></span>
<span className="font-label-sm text-label-sm text-primary-container font-mono font-bold">FLIGHT-A // WINGMAN</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-7112]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">2nd Lt. M. Chen</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "VIPER-4"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-primary-container/40 text-primary-container font-label-sm text-label-sm font-bold font-mono">CR-1 FULL</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-primary font-bold">Sensor-to-Shoot High Latency Ingress</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">21</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-primary-container font-bold">94.6%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-primary-container font-bold">92%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-primary font-bold">1.76s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-primary-container flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">verified</span> COMBAT MISSION READY
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: 2nd Lt. M. Chen (VIPER-4)')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-primary-container hover:text-on-primary text-secondary font-label-sm text-label-sm uppercase font-mono" onclick="alert('Pilot Chen attached to Phantoms Wing-1.')" type="button">Profile</button>
</div>
</div>
</div>
{/*  PILOT 3 (Flight A Prov)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-tertiary-fixed-dim transition-all flex flex-col justify-between" data-flight="flight-a" data-name="Patel" data-status="CR-2">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-tertiary-fixed-dim"></span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-mono font-bold">FLIGHT-A // ROTATION</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-7189]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">Ens. D. Patel</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "HALO-09"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-tertiary-fixed-dim/50 text-tertiary-fixed-dim font-label-sm text-label-sm font-bold font-mono">CR-2 PROV</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-on-surface font-bold">Kinetic Point Defense Escort</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">14</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-primary-container font-bold">89.0%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-tertiary-fixed-dim font-bold">84%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-tertiary-fixed-dim font-bold">2.12s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">schedule</span> PROVISIONAL STATUS
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Ens. D. Patel (HALO-09)')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-tertiary-container hover:text-on-tertiary-container text-tertiary-fixed-dim font-label-sm text-label-sm uppercase font-mono" onclick="alert('Scheduling Solo Escort Evaluation for Ens. Patel')" type="button">Sched Re-Test</button>
</div>
</div>
</div>
{/*  PILOT 4 (Flight B Lead)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-error transition-all flex flex-col justify-between" data-flight="flight-b" data-name="Miller" data-status="CR-2">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-error"></span>
<span className="font-label-sm text-label-sm text-error font-mono font-bold">FLIGHT-B // LEAD</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8842]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">Lt. J. Miller</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "TALON-LEAD"</span>
</div>
<span className="px-space-xs py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold font-mono">CR-2 PROV</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-on-surface font-bold">Multi-Axis Low-Alt Intercept</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">19</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-tertiary-fixed-dim font-bold">85.4%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-error font-bold">68%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-error font-bold">2.28s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-error flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">warning</span> REMEDIATION FLAG
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Lt. J. Miller (TALON-LEAD)')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-error-container hover:bg-error hover:text-surface text-on-error-container font-label-sm text-label-sm uppercase font-mono font-bold" onclick="alert('Scheduled intensive Mode-4 Anti-Spoof Re-Test with Evaluator Vance.')" type="button">Sched Re-Test</button>
</div>
</div>
</div>
{/*  PILOT 5 (Flight B Deficit)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-error transition-all flex flex-col justify-between" data-flight="flight-b" data-name="Briggs" data-status="CR-3">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-error animate-pulse"></span>
<span className="font-label-sm text-label-sm text-error font-mono font-bold">FLIGHT-B // CRITICAL DEFICIT</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8861]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-error mt-0.5">Capt. T. Briggs</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "RAZOR-07"</span>
</div>
<span className="px-space-xs py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold font-mono">CR-3 DEFICIT</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-error font-bold">Swarm Suppression [HOLD REQ]</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">12</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-error font-bold">71.0%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-error font-bold">54%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-error font-bold">2.65s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-error flex items-center gap-1 font-mono font-bold">
<span className="material-symbols-outlined text-[12px]">block</span> FLIGHT LOCKOUT ACTIVE
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Capt. T. Briggs. Lockout enforced per STANAG Directive 03.')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-error text-surface font-label-sm text-label-sm uppercase font-mono font-bold" onclick="alert('Enqueuing pilot Briggs into Anti-Spoof Sim Deck B.')" type="button">Recert Now</button>
</div>
</div>
</div>
{/*  PILOT 6 (Flight B Deficit 2)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-error transition-all flex flex-col justify-between" data-flight="flight-b" data-name="Kowalski" data-status="CR-3">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-error animate-pulse"></span>
<span className="font-label-sm text-label-sm text-error font-mono font-bold">FLIGHT-B // CRITICAL DEFICIT</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8874]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-error mt-0.5">Lt. S. Kowalski</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "TALON-05"</span>
</div>
<span className="px-space-xs py-0.5 bg-error-container text-on-error-container font-label-sm text-label-sm font-bold font-mono">CR-3 DEFICIT</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-error font-bold">Close-Proximity Drone Engagement</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">11</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-error font-bold">69.5%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-error font-bold">58%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-error font-bold">2.70s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-error flex items-center gap-1 font-mono font-bold">
<span className="material-symbols-outlined text-[12px]">block</span> FLIGHT LOCKOUT ACTIVE
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Lt. S. Kowalski.')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-error text-surface font-label-sm text-label-sm uppercase font-mono font-bold" onclick="alert('Enqueuing pilot Kowalski for Decoy Discrimination drill.')" type="button">Recert Now</button>
</div>
</div>
</div>
{/*  PILOT 7 (Flight C Lead - EW Master)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-secondary-container transition-all flex flex-col justify-between" data-flight="flight-c" data-name="Tarasov" data-status="CR-1">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-secondary-container"></span>
<span className="font-label-sm text-label-sm text-secondary-container font-mono font-bold">FLIGHT-C // LEAD &amp; EW DIR</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8339]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">WO1 K. Tarasov</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "SPECTRE-LEAD"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-secondary-container/50 text-secondary-container font-label-sm text-label-sm font-bold font-mono">CR-1 FULL</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-secondary-container font-bold">Directed RF Jammer / Null Beamforming</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">26</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-secondary-container font-bold">96.8%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-secondary-container font-bold">98%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-secondary font-bold">1.20s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-secondary-container flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">security</span> EW MASTER INSTRUCTOR
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: WO1 K. Tarasov (SPECTRE-LEAD). Top EW Operator.')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-secondary-container hover:bg-white text-on-secondary font-label-sm text-label-sm uppercase font-mono font-bold" onclick="alert('Directive 01 Executed: Cross-attaching WO1 Tarasov to Flight-B for Anti-Spoof Tutelage.')" type="button">Cross-Attach</button>
</div>
</div>
</div>
{/*  PILOT 8 (Flight C Wingman)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-secondary-container transition-all flex flex-col justify-between" data-flight="flight-c" data-name="Nakamura" data-status="CR-1">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-secondary-container"></span>
<span className="font-label-sm text-label-sm text-secondary-container font-mono font-bold">FLIGHT-C // OPERATOR</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8344]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">Capt. H. Nakamura</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "SHADOW-03"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-secondary-container/50 text-secondary-container font-label-sm text-label-sm font-bold font-mono">CR-1 FULL</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-secondary font-bold">Broadband Strobe &amp; RF Countermeasures</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">18</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-secondary-container font-bold">92.0%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-secondary-container font-bold">91%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-primary font-bold">1.88s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-secondary-container flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">verified</span> EW QUALIFIED
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Capt. H. Nakamura')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-secondary font-label-sm text-label-sm uppercase font-mono" onclick="alert('Operator profile loaded.')" type="button">Profile</button>
</div>
</div>
</div>
{/*  PILOT 9 (Flight C Prov)  */}
<div className="pilot-card bg-surface-container-lowest p-space-sm border border-outline-variant hover:border-tertiary-fixed-dim transition-all flex flex-col justify-between" data-flight="flight-c" data-name="Larsson" data-status="CR-2">
<div>
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-space-xs">
<span className="w-2 h-2 bg-tertiary-fixed-dim"></span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-mono font-bold">FLIGHT-C // ROTATION</span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">[TRN-8392]</span>
</div>
<h3 className="font-headline-sm text-headline-sm text-on-background mt-0.5">Lt. E. Larsson</h3>
<span className="font-label-sm text-label-sm text-secondary font-mono">CALLSIGN: "PULSE-08"</span>
</div>
<span className="px-space-xs py-0.5 bg-surface-container-high border border-tertiary-fixed-dim/50 text-tertiary-fixed-dim font-label-sm text-label-sm font-bold font-mono">CR-2 PROV</span>
</div>
<div className="mt-space-xs py-space-xs px-space-sm bg-surface-container flex items-center justify-between text-label-sm font-label-sm">
<span className="text-on-surface-variant">SPEC:</span>
<span className="text-on-surface font-bold">Telemetry Link &amp; Relay Defense</span>
</div>
<div className="mt-space-xs grid grid-cols-4 gap-space-xs text-center font-mono">
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">SORTIES</span><span className="text-label-md text-primary font-bold">15</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">INTERCEPT</span><span className="text-label-md text-tertiary-fixed-dim font-bold">86.2%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">IFF DISCR</span><span className="text-label-md text-secondary-container font-bold">88%</span></div>
<div className="bg-surface-container p-1"><span className="block text-[10px] text-on-surface-variant">LATENCY</span><span className="text-label-md text-tertiary-fixed-dim font-bold">2.25s</span></div>
</div>
</div>
<div className="mt-space-sm pt-space-xs border-t border-outline-variant flex items-center justify-between gap-space-xs">
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim flex items-center gap-1 font-mono">
<span className="material-symbols-outlined text-[12px]">schedule</span> PROVISIONAL STATUS
</span>
<div className="flex items-center gap-1">
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-bright text-on-surface font-label-sm text-label-sm uppercase font-mono" onclick="alert('Viewing Dossier: Lt. E. Larsson')" type="button">Dossier</button>
<button className="px-space-xs py-0.5 bg-surface-container-high hover:bg-tertiary-container hover:text-on-tertiary-container text-tertiary-fixed-dim font-label-sm text-label-sm uppercase font-mono" onclick="alert('Scheduling Beamforming recertification test.')" type="button">Sched Re-Test</button>
</div>
</div>
</div>
</div>
{/*  Empty State fallback  */}
<div className="hidden mt-space-md p-space-lg bg-surface-container-lowest text-center border border-dashed border-outline-variant" id="roster-empty-state">
<span className="material-symbols-outlined text-[32px] text-on-surface-variant">person_search</span>
<p className="font-label-md text-label-md text-on-surface mt-1 uppercase">No Pilots match current flight / status filter combination</p>
<button className="mt-space-sm px-space-sm py-1 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold uppercase" onclick="resetFilters()" type="button">Clear Filter Constraints</button>
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
<span className="flex items-center gap-1 cursor-pointer hover:underline" onclick="selectFlightFilter('flight-a')"><span className="w-2.5 h-2.5 bg-primary-container inline-block"></span> Phantoms (A)</span>
<span className="flex items-center gap-1 cursor-pointer hover:underline" onclick="selectFlightFilter('flight-b')"><span className="w-2.5 h-2.5 bg-error inline-block"></span> Talons (B)</span>
<span className="flex items-center gap-1 cursor-pointer hover:underline" onclick="selectFlightFilter('flight-c')"><span className="w-2.5 h-2.5 bg-secondary-container inline-block"></span> Reapers (C)</span>
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
{/*  Interactive Roster Logic Script  */}


    </div>
  );
}
