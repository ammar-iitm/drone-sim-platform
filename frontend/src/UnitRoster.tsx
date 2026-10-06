import React from 'react';

export default function UnitRoster() {
  return (
    <div className="dark h-full overflow-y-auto">
      <header className="fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant z-50 flex items-center justify-between px-space-md"><div className="flex items-center gap-space-md"><div className="flex items-center gap-space-sm pl-space-xs"><span className="material-symbols-outlined text-primary-container text-[20px]">radar</span><span className="font-label-lg text-label-lg tracking-wider text-primary uppercase">AEGIS // C2 SIMULATION</span></div><span className="px-space-sm py-space-xs bg-surface-container text-on-surface-variant font-label-sm text-label-sm border border-outline-variant uppercase">UNCLASSIFIED // EXERCISE USE ONLY</span></div><div className="flex items-center gap-space-lg"><div className="flex items-center gap-space-sm px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">DEFCON</span><span className="font-telemetry-data text-telemetry-data text-primary-container font-bold">4-READY</span></div><div className="flex items-center gap-space-xs font-label-md text-label-md px-space-sm py-space-xs bg-surface-container-lowest border border-outline-variant"><span className="material-symbols-outlined text-[16px] text-secondary-container">timer</span><span className="text-on-surface-variant font-label-sm text-label-sm">T+</span><span className="font-telemetry-data text-telemetry-data text-secondary-container">02:44:18.4Z</span></div><div className="flex items-center gap-space-sm"><button className="flex items-center gap-space-xs px-space-sm py-space-xs border border-outline-variant hover:bg-surface-container hover:text-on-surface text-on-surface-variant transition-colors" title="Audio/Comms Channel" type="button"><span className="material-symbols-outlined text-[16px]">volume_up</span><span className="font-label-sm text-label-sm uppercase">NET-1 CH-A</span></button><div className="px-space-sm py-space-xs bg-surface-container border border-outline-variant"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INST: </span><span className="font-label-sm text-label-sm text-primary">MAJ. VANCE [TAC-01]</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div></header><a href="#"side className="fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low border-r border-outline-variant z-40 flex flex-col justify-between"><div className="flex flex-col"><div className="px-space-md py-space-sm border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between"><span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">C2 OPERATIONAL RAIL</span><span className="font-label-sm text-label-sm text-primary-container font-bold">ONLINE</span></div><nav className="flex flex-col py-space-xs" data-active-classes="bg-surface-container text-primary-container font-bold border-l-2 border-primary-container"><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="live-instructor-dashboard" href="#"><span>Live Dashboard</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="scenario-builder" href="#"><span>Scenario Builder</span></a><a className="flex items-center px-space-md py-space-md text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-all font-label-md text-label-md uppercase" data-path="aar-reports" href="#"><span>AAR Reports</span></a><a aria-current="page" className="flex items-center px-space-md py-space-md transition-all uppercase bg-surface-container text-primary-container font-bold border-l-2 border-primary-container" data-path="unit-roster" href="#"><span>Unit Roster</span></a></nav></div><div className="p-space-md border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-space-xs"><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm"><span className="uppercase">SWARM TELEM</span><span className="text-primary-container font-telemetry-data text-telemetry-data">48 UCAV</span></div><div className="w-full bg-surface-container-highest h-1"><div className="bg-primary-container h-1 w-3/4"></div></div><div className="flex justify-between items-center text-on-surface-variant font-label-sm text-label-sm mt-space-xs"><span>GRID REF: 38TLN 4289</span><span>LATENCY: 12ms</span></div></div></aside><div className="pl-60"><main className="w-full pt-14 bg-surface min-h-screen"><div className="flex flex-col w-full">
{/*  SUB-HEADER / C2 SQUADRON READINESS CONTROL BAR  */}
<div className="w-full bg-surface-container-lowest border-b border-outline-variant px-space-md py-space-sm flex flex-col xl:flex-row xl:items-center justify-between gap-space-sm">
<div className="flex flex-col gap-space-xs">
<div className="flex items-center gap-space-sm">
<span className="inline-block w-2.5 h-2.5 bg-primary-container animate-pulse"></span>
<h1 className="font-headline-md text-headline-md tracking-wider text-primary uppercase">
          UNIT ROSTER // 104TH TACTICAL UAS INTERCEPT SQUADRON
        </h1>
<span className="px-space-sm py-0.5 bg-surface-container border border-outline-variant font-label-sm text-label-sm text-secondary-container tracking-widest uppercase">
          STANAG-4586 // NATO SEC-IV
        </span>
</div>
<div className="flex flex-wrap items-center gap-x-space-md gap-y-0.5 font-label-sm text-label-sm text-on-surface-variant">
<span>ECHELON: <strong className="text-on-surface font-telemetry-data">BATTALION C2</strong></span>
<span className="text-outline-variant">•</span>
<span>ACTIVE PILOTS: <strong className="text-on-surface font-telemetry-data">28</strong></span>
<span className="text-outline-variant">•</span>
<span>COMBAT QUALIFIED (CR-1): <strong className="text-primary-container font-telemetry-data">19 (68%)</strong></span>
<span className="text-outline-variant">•</span>
<span>READINESS DEFICIT: <span className="text-error-container font-telemetry-data font-bold text-error bg-error-container/20 px-1">4 PILOTS [CR-2/CR-4]</span></span>
</div>
</div>
{/*  TACTICAL ACTIONS ROW  */}
<div className="flex flex-wrap items-center gap-space-xs">
<div className="relative flex items-center">
<span className="material-symbols-outlined text-[15px] absolute left-2 text-on-surface-variant">search</span>
<input className="bg-surface-container-low border border-outline-variant pl-7 pr-3 py-1 font-label-sm text-label-sm text-on-surface placeholder:text-outline focus:outline-none focus:border-secondary-container w-48 sm:w-56" placeholder="SEARCH CALLSIGN / TRN ID..." type="text"/>
</div>
<div className="relative inline-block">
<button className="flex items-center gap-1 px-space-sm py-1 bg-surface-container-low border border-outline-variant font-label-sm text-label-sm text-on-surface hover:bg-surface-container transition-colors uppercase" type="button">
<span>FLIGHT: ALL</span>
<span className="material-symbols-outlined text-[14px] text-secondary-container">arrow_drop_down</span>
</button>
</div>
<button className="flex items-center gap-1 px-space-sm py-1 bg-surface-container-low border border-outline-variant font-label-sm text-label-sm text-on-surface hover:bg-surface-container transition-colors uppercase" type="button">
<span className="material-symbols-outlined text-[14px] text-secondary-container">file_download</span>
<span>EXPORT QUALS</span>
</button>
<button className="flex items-center gap-1 px-space-md py-1 bg-primary-container text-on-primary font-label-sm text-label-sm font-bold hover:brightness-110 transition-all uppercase shadow-[0_0_8px_rgba(0,255,102,0.3)]" type="button">
<span className="material-symbols-outlined text-[14px]">person_add</span>
<span>INDUCT TRAINEE</span>
</button>
</div>
</div>
{/*  MAIN OPERATIONAL DUAL-PANE WORKSPACE  */}
<div className="grid grid-cols-1 lg:grid-cols-12 w-full gap-0 bg-surface">
{/*  LEFT COLUMN: SQUADRON ROSTER DIRECTORY & PIPELINE (35% -> 4 cols on 12-col grid)  */}
<a href="#"side className="lg:col-span-4 xl:col-span-4 border-r border-outline-variant bg-surface-container-low flex flex-col justify-between">
<div className="flex flex-col">
{/*  Sub-panel Tag Header  */}
<div className="px-space-md py-space-xs bg-surface-container-lowest border-b border-outline-variant flex items-center justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
            ROSTER DIRECTORY // 28 ACTIVE OPERATORS
          </span>
<span className="font-label-sm text-label-sm text-secondary-container font-mono">SORT: STATUS_DESC</span>
</div>
{/*  Filter Segmented Bar  */}
<div className="grid grid-cols-5 border-b border-outline-variant bg-surface-container-lowest text-center">
<button className="py-1.5 font-label-sm text-label-sm font-bold text-primary-container bg-surface-container-low border-b-2 border-primary-container uppercase">
            ALL (28)
          </button>
<button className="py-1.5 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface transition-colors uppercase">
            FLT-A (9)
          </button>
<button className="py-1.5 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface transition-colors uppercase">
            FLT-B (10)
          </button>
<button className="py-1.5 font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface transition-colors uppercase">
            FLT-C (9)
          </button>
<button className="py-1.5 font-label-sm text-label-sm text-error hover:text-on-error-container transition-colors uppercase">
            HOLD (3)
          </button>
</div>
{/*  Trainee Interactive Cards List  */}
<div className="flex flex-col divide-y divide-outline-variant overflow-y-auto max-h-[calc(100vh-14rem)]">
{/*  CARD 1: ACTIVE / SELECTED (LT. J. MILLER)  */}
<div className="p-space-sm bg-surface-container border-l-4 border-primary-container cursor-pointer transition-all hover:bg-surface-container-high relative">
<div className="absolute top-1 right-2 flex items-center gap-1">
<span className="w-1.5 h-1.5 rounded-full bg-tertiary-fixed-dim animate-ping"></span>
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim px-1 bg-on-tertiary/60 border border-tertiary-fixed-dim/40">
                CR-2 PROVISIONAL
              </span>
</div>
<div className="flex items-start gap-space-sm pr-20">
<div className="w-8 h-8 bg-surface-container-highest border border-outline-variant flex items-center justify-center font-label-sm text-label-sm font-bold text-primary shrink-0">
                O-2
              </div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-primary tracking-tight font-bold truncate">LT. J. MILLER</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TRN-8842</span>
</div>
<div className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant">
<span>CALLSIGN: <span className="text-secondary-container font-mono">VANGUARD-3</span></span>
<span>•</span>
<span>FLIGHT-B</span>
</div>
</div>
</div>
{/*  Card Telemetry Line  */}
<div className="mt-2 pt-2 border-t border-outline-variant/60 grid grid-cols-3 gap-1 font-label-sm text-label-sm">
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px] uppercase">SIM TIME</span>
<span className="font-telemetry-data text-on-surface">142.5h</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px] uppercase">COMPOSITE</span>
<span className="font-telemetry-data text-primary-container">84.2% [B+]</span>
</div>
<div className="flex flex-col text-right">
<span className="text-on-surface-variant text-[8px] uppercase">LAST EX</span>
<span className="font-telemetry-data text-tertiary-fixed-dim">EX-2025-048</span>
</div>
</div>
{/*  Alert Banner In Card  */}
<div className="mt-1.5 px-1.5 py-0.5 bg-on-tertiary/40 border border-tertiary-fixed-dim/30 flex items-center justify-between">
<span className="font-label-sm text-[8px] text-tertiary-fixed-dim uppercase tracking-tight truncate">REMEDIATION: SPOOFED IFF DISCRIM</span>
<span className="material-symbols-outlined text-[12px] text-tertiary-fixed-dim">warning</span>
</div>
</div>
{/*  CARD 2: CAPT. R. STERLING  */}
<div className="p-space-sm bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer border-l-4 border-transparent">
<div className="flex items-start justify-between">
<div className="flex items-start gap-space-sm">
<div className="w-8 h-8 bg-surface-container-highest border border-outline-variant flex items-center justify-center font-label-sm text-label-sm font-bold text-primary-container shrink-0">
                  O-3
                </div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold truncate">CAPT. R. STERLING</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TRN-7104</span>
</div>
<div className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant">
<span>CALLSIGN: <span className="text-secondary-container font-mono">WARHAMMER-1</span></span>
<span>•</span>
<span>FLT-A [LEAD]</span>
</div>
</div>
</div>
<span className="font-label-sm text-label-sm text-primary-container px-1 bg-surface-container-lowest border border-primary-container/40">
                CR-1 FULL
              </span>
</div>
<div className="mt-2 grid grid-cols-3 gap-1 font-label-sm text-label-sm">
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">SIM TIME</span>
<span className="font-telemetry-data text-on-surface">320.0h</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">COMPOSITE</span>
<span className="font-telemetry-data text-primary-container">96.4% [A+]</span>
</div>
<div className="flex flex-col text-right">
<span className="text-on-surface-variant text-[8px]">STATUS</span>
<span className="font-label-sm text-[9px] text-primary-container font-bold">COMBAT READY</span>
</div>
</div>
</div>
{/*  CARD 3: 2ND LT. M. CHEN  */}
<div className="p-space-sm bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer border-l-4 border-transparent">
<div className="flex items-start justify-between">
<div className="flex items-start gap-space-sm">
<div className="w-8 h-8 bg-surface-container-highest border border-outline-variant flex items-center justify-center font-label-sm text-label-sm font-bold text-on-surface-variant shrink-0">
                  O-1
                </div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold truncate">2ND LT. M. CHEN</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TRN-9021</span>
</div>
<div className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant">
<span>CALLSIGN: <span className="text-secondary-container font-mono">SPECTER-6</span></span>
<span>•</span>
<span>FLT-B</span>
</div>
</div>
</div>
<span className="font-label-sm text-label-sm text-secondary px-1 bg-surface-container-lowest border border-secondary/40">
                CR-3 APPR
              </span>
</div>
<div className="mt-2 grid grid-cols-3 gap-1 font-label-sm text-label-sm">
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">SIM TIME</span>
<span className="font-telemetry-data text-on-surface">68.0h</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">COMPOSITE</span>
<span className="font-telemetry-data text-on-surface">71.8% [C]</span>
</div>
<div className="flex flex-col text-right">
<span className="text-on-surface-variant text-[8px]">STATUS</span>
<span className="font-label-sm text-[9px] text-secondary">SWARM DRILL</span>
</div>
</div>
</div>
{/*  CARD 4: WO1 K. TARASOV  */}
<div className="p-space-sm bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer border-l-4 border-transparent">
<div className="flex items-start justify-between">
<div className="flex items-start gap-space-sm">
<div className="w-8 h-8 bg-surface-container-highest border border-outline-variant flex items-center justify-center font-label-sm text-label-sm font-bold text-secondary-container shrink-0">
                  W-1
                </div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold truncate">WO1 K. TARASOV</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TRN-8339</span>
</div>
<div className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant">
<span>CALLSIGN: <span className="text-secondary-container font-mono">GHOST-4</span></span>
<span>•</span>
<span>FLT-C</span>
</div>
</div>
</div>
<span className="font-label-sm text-label-sm text-primary-container px-1 bg-surface-container-lowest border border-primary-container/40">
                CR-1 FULL
              </span>
</div>
<div className="mt-2 grid grid-cols-3 gap-1 font-label-sm text-label-sm">
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">SIM TIME</span>
<span className="font-telemetry-data text-on-surface">215.2h</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">COMPOSITE</span>
<span className="font-telemetry-data text-primary-container">91.0% [A]</span>
</div>
<div className="flex flex-col text-right">
<span className="text-on-surface-variant text-[8px]">SPEC</span>
<span className="font-label-sm text-[9px] text-primary">EW CERTIFIED</span>
</div>
</div>
</div>
{/*  CARD 5: ENS. D. PATEL  */}
<div className="p-space-sm bg-surface-container-low hover:bg-surface-container transition-colors cursor-pointer border-l-4 border-transparent">
<div className="flex items-start justify-between">
<div className="flex items-start gap-space-sm">
<div className="w-8 h-8 bg-surface-container-highest border border-outline-variant flex items-center justify-center font-label-sm text-label-sm font-bold text-error shrink-0">
                  O-1
                </div>
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold truncate">ENS. D. PATEL</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">TRN-9410</span>
</div>
<div className="flex items-center gap-2 font-label-sm text-label-sm text-on-surface-variant">
<span>CALLSIGN: <span className="text-secondary-container font-mono">ANVIL-2</span></span>
<span>•</span>
<span>FLT-A</span>
</div>
</div>
</div>
<span className="font-label-sm text-label-sm text-error px-1 bg-surface-container-lowest border border-error/40">
                CR-4 UNQUAL
              </span>
</div>
<div className="mt-2 grid grid-cols-3 gap-1 font-label-sm text-label-sm">
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">SIM TIME</span>
<span className="font-telemetry-data text-on-surface">34.0h</span>
</div>
<div className="flex flex-col">
<span className="text-on-surface-variant text-[8px]">COMPOSITE</span>
<span className="font-telemetry-data text-error">62.5% [D]</span>
</div>
<div className="flex flex-col text-right">
<span className="text-on-surface-variant text-[8px]">ALERT</span>
<span className="font-label-sm text-[9px] text-error font-bold truncate">OVERLOAD</span>
</div>
</div>
</div>
</div>
</div>
{/*  Quick Squadron Stats Dock (Sticky Bottom Left)  */}
<div className="p-space-sm border-t border-outline-variant bg-surface-container-lowest flex flex-col gap-1 font-label-sm text-label-sm">
<div className="flex justify-between items-center text-on-surface-variant">
<span>FLEET COMPOSITE AVG:</span>
<span className="font-telemetry-data text-primary-container">81.4%</span>
</div>
<div className="flex justify-between items-center text-on-surface-variant">
<span>MEAN REACTION TIME:</span>
<span className="font-telemetry-data text-secondary-container">2.94s</span>
</div>
<div className="w-full bg-surface-container-highest h-1 mt-0.5">
<div className="bg-primary-container h-1 w-[81.4%]"></div>
</div>
</div>
</aside>
{/*  RIGHT COLUMN: MASTER DETAIL TRAINEE PROFILE DOSSIER (65% -> 8 cols)  */}
<section className="lg:col-span-8 xl:col-span-8 bg-surface flex flex-col divide-y divide-outline-variant">
{/*  SECTION 1: TRAINEE BIO & TOP METRICS HEADER  */}
<div className="p-space-md bg-surface-container-lowest flex flex-col gap-space-md">
<div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md">
{/*  Identity Info with Pilot Silhouette/Avatar  */}
<div className="flex items-center gap-space-md">
<div className="relative w-16 h-16 bg-surface-container border-2 border-outline-variant flex items-center justify-center overflow-hidden shrink-0">
<span className="material-symbols-outlined text-[42px] text-outline">account_circle</span>
<div className="absolute bottom-0 inset-x-0 bg-surface-container-highest/90 text-center font-label-sm text-[8px] text-primary">
                O-2 USAF
              </div>
</div>
<div className="flex flex-col">
<div className="flex items-center gap-space-sm">
<h2 className="font-headline-lg text-headline-lg text-primary tracking-wide font-bold">
                  LT. JONATHAN MILLER
                </h2>
<span className="px-space-xs py-0.5 bg-surface-container border border-outline font-label-sm text-label-sm text-secondary-container">
                  TRN-8842-USAF
                </span>
</div>
<div className="flex flex-wrap items-center gap-x-space-md gap-y-0.5 mt-0.5 font-label-sm text-label-sm text-on-surface-variant">
<span>TACTICAL CALLSIGN: <strong className="text-primary font-mono font-bold">VANGUARD-3</strong></span>
<span>•</span>
<span>ASSIGNED: <strong className="text-on-surface">FLIGHT-B "TALONS"</strong></span>
<span>•</span>
<span>CONSOLE: <strong className="text-on-surface">C2 STATION ALPHA-04</strong></span>
</div>
</div>
</div>
{/*  Large Mil-Spec Readiness Stamp Badge  */}
<div className="px-space-md py-space-xs border-2 border-tertiary-fixed-dim bg-on-tertiary/20 flex flex-col items-center justify-center shrink-0">
<span className="font-label-sm text-[8px] tracking-widest text-tertiary-fixed-dim uppercase">READINESS STATUS EVAL</span>
<span className="font-label-lg text-label-lg font-bold text-tertiary-fixed tracking-wider uppercase">
              CR-2 [RESTRICTED ESCORT]
            </span>
<span className="font-label-sm text-[8px] text-on-surface-variant uppercase">STANAG-4586 LVL-3 CERT</span>
</div>
</div>
{/*  5 High-Density Metric Counters  */}
<div className="grid grid-cols-2 sm:grid-cols-5 gap-space-xs pt-space-xs">
<div className="bg-surface-container-low border border-outline-variant p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SIM HOURS</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-primary">142.5</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">/ 150h</span>
</div>
<div className="w-full bg-surface-container h-1 mt-1">
<div className="bg-primary-container h-1 w-[95%]"></div>
</div>
</div>
<div className="bg-surface-container-low border border-outline-variant p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">SCENARIOS</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-on-surface">46</span>
<span className="font-label-sm text-label-sm text-primary-container font-mono">38P/6M</span>
</div>
<span className="font-label-sm text-[9px] text-on-surface-variant">2 FAILED RUNS</span>
</div>
<div className="bg-surface-container-low border border-outline-variant p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">NEUTRALIZED</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-secondary-container">412</span>
<span className="font-label-sm text-label-sm text-on-surface-variant">UCAV</span>
</div>
<span className="font-label-sm text-[9px] text-on-surface-variant">248 KIN / 164 EW</span>
</div>
<div className="bg-surface-container-low border border-outline-variant p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">INGRESS LATENCY</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-primary-container">2.18s</span>
</div>
<span className="font-label-sm text-[9px] text-primary-container">EXCEEDS (&lt;3.50s)</span>
</div>
<div className="bg-surface-container-low border border-outline-variant p-space-sm flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">STRESS RECOV</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-critical text-telemetry-critical text-on-surface">11.4s</span>
</div>
<span className="font-label-sm text-[9px] text-on-surface-variant">NOMINAL BAND</span>
</div>
</div>
</div>
{/*  SECTION 2: CUMULATIVE COMPETENCY RADAR & CORE PILLARS BREAKDOWN  */}
<div className="p-space-md bg-surface-container-low flex flex-col gap-space-sm">
<div className="flex items-center justify-between border-b border-outline-variant pb-space-xs">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-primary-container">tune</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wide">
              CORE COMPETENCY PILLARS // STANAG EVALUATION CRITERIA
            </span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant">BENCHMARK: 80% MINIMUM CR-1 PASS</span>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 gap-space-md pt-space-xs">
{/*  Pillar 1: Threat Detection  */}
<div className="flex flex-col gap-1 p-space-sm bg-surface-container border border-outline-variant">
<div className="flex justify-between items-center">
<span className="font-body-md text-body-md text-on-surface font-semibold">1. Threat Detection &amp; Ingress Recognition</span>
<span className="font-telemetry-data text-primary-container font-bold">92%</span>
</div>
<div className="w-full bg-surface-container-highest h-2">
<div className="bg-primary-container h-2 w-[92%]"></div>
</div>
<div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant pt-0.5">
<span>BENCHMARK: 80%</span>
<span className="text-primary-container font-bold uppercase">[EXCEEDS SPEC]</span>
</div>
</div>
{/*  Pillar 2: IFF Discrimination (DEFICIENT CRITICAL ALERT)  */}
<div className="flex flex-col gap-1 p-space-sm bg-surface-container border border-error/50 relative overflow-hidden">
<div className="absolute right-0 top-0 bottom-0 w-1 bg-error"></div>
<div className="flex justify-between items-center">
<span className="font-body-md text-body-md text-error font-semibold flex items-center gap-1">
<span className="material-symbols-outlined text-[14px]">error</span>
                2. IFF Discrimination &amp; Deception Resistance
              </span>
<span className="font-telemetry-data text-error font-bold">64%</span>
</div>
<div className="w-full bg-surface-container-highest h-2">
<div className="bg-error h-2 w-[64%]"></div>
</div>
<div className="flex justify-between items-center font-label-sm text-label-sm pt-0.5">
<span className="text-on-surface-variant">BENCHMARK: 85% MANDATORY</span>
<span className="text-error font-bold uppercase">[DEFICIENT - RETRAIN]</span>
</div>
<div className="font-label-sm text-[9px] text-tertiary-fixed-dim bg-surface-container-lowest/80 px-1.5 py-0.5 mt-1 border border-outline-variant">
              CRITICAL: Failed Mode-4 Spoofing in SIM-EX-2025-048 (Late CIWS unlock)
            </div>
</div>
{/*  Pillar 3: Kinetic CIWS Interception  */}
<div className="flex flex-col gap-1 p-space-sm bg-surface-container border border-outline-variant">
<div className="flex justify-between items-center">
<span className="font-body-md text-body-md text-on-surface font-semibold">3. Swarm Vector &amp; Kinetic CIWS Interception</span>
<span className="font-telemetry-data text-primary-container font-bold">88%</span>
</div>
<div className="w-full bg-surface-container-highest h-2">
<div className="bg-primary-container h-2 w-[88%]"></div>
</div>
<div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant pt-0.5">
<span>BENCHMARK: 75%</span>
<span className="text-primary font-bold uppercase">[PROFICIENT]</span>
</div>
</div>
{/*  Pillar 4: Directed RF & ECM  */}
<div className="flex flex-col gap-1 p-space-sm bg-surface-container border border-outline-variant">
<div className="flex justify-between items-center">
<span className="font-body-md text-body-md text-on-surface font-semibold">4. Directed RF &amp; Electronic Countermeasures</span>
<span className="font-telemetry-data text-secondary-container font-bold">86%</span>
</div>
<div className="w-full bg-surface-container-highest h-2">
<div className="bg-secondary-container h-2 w-[86%]"></div>
</div>
<div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant pt-0.5">
<span>BENCHMARK: 80%</span>
<span className="text-secondary-container font-bold uppercase">[PROFICIENT]</span>
</div>
</div>
{/*  Pillar 5: Multi-Axis Stress Composure (Spans 2 cols on md)  */}
<div className="md:col-span-2 flex flex-col gap-1 p-space-sm bg-surface-container border border-outline-variant">
<div className="flex justify-between items-center">
<span className="font-body-md text-body-md text-on-surface font-semibold">5. High-Stress Multi-Axis Composure &amp; Salvo Throttle</span>
<span className="font-telemetry-data text-on-surface font-bold">76%</span>
</div>
<div className="w-full bg-surface-container-highest h-2">
<div className="bg-outline h-2 w-[76%]"></div>
</div>
<div className="flex justify-between items-center font-label-sm text-label-sm text-on-surface-variant pt-0.5">
<span>BENCHMARK: 75% SPEC STANDARD</span>
<span className="text-on-surface font-bold uppercase">[COMPETENT]</span>
</div>
</div>
</div>
</div>
{/*  SECTION 3: SIMULATION MISSION HISTORY & FLIGHT LOG TABLE  */}
<div className="p-space-md bg-surface flex flex-col gap-space-sm">
<div className="flex items-center justify-between border-b border-outline-variant pb-space-xs">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-secondary-container">history_edu</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wide">
              RECENT SIMULATION SORTIES // BLACKBOX TELEMETRY LOG
            </span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">RECORDS: 4 OF 46 DISPLAYED</span>
</div>
<div className="overflow-x-auto w-full">
<table className="w-full text-left border-collapse">
<thead>
<tr className="border-b border-outline-variant bg-surface-container-lowest text-on-surface-variant font-label-sm text-label-sm uppercase">
<th className="py-2 px-3">SIM SORTIE ID</th>
<th className="py-2 px-3">DATE (ZULU)</th>
<th className="py-2 px-3">SCENARIO DESIGNATION</th>
<th className="py-2 px-3 text-right">GRADE</th>
<th className="py-2 px-3">FAULTS DETECTED</th>
<th className="py-2 px-3">STATUS</th>
<th className="py-2 px-3 text-right">ACTION</th>
</tr>
</thead>
<tbody className="divide-y divide-outline-variant font-body-sm text-body-sm">
{/*  Log Row 1 (Marginal)  */}
<tr className="bg-surface-container-low hover:bg-surface-container transition-colors">
<td className="py-2.5 px-3 font-telemetry-data text-primary">SIM-EX-2025-048</td>
<td className="py-2.5 px-3 font-mono text-on-surface-variant">2025-10-24</td>
<td className="py-2.5 px-3 font-medium text-on-surface">Op-Viper Strike (Phase 02)</td>
<td className="py-2.5 px-3 text-right font-telemetry-data text-tertiary-fixed-dim">82.4% [B+]</td>
<td className="py-2.5 px-3">
<span className="px-1.5 py-0.5 bg-error-container/30 border border-error text-error font-label-sm text-[9px] uppercase">
                    1 CRITICAL (IFF SPOOF)
                  </span>
</td>
<td className="py-2.5 px-3 font-label-sm text-label-sm text-tertiary-fixed-dim font-bold">QUAL [MARGINAL]</td>
<td className="py-2.5 px-3 text-right">
<button className="text-secondary-container hover:underline font-label-sm text-label-sm uppercase font-mono" type="button">
                    [AAR DEBRIEF]
                  </button>
</td>
</tr>
{/*  Log Row 2 (Excellent)  */}
<tr className="bg-surface hover:bg-surface-container transition-colors">
<td className="py-2.5 px-3 font-telemetry-data text-primary">SIM-EX-2025-041</td>
<td className="py-2.5 px-3 font-mono text-on-surface-variant">2025-10-18</td>
<td className="py-2.5 px-3 font-medium text-on-surface">Swarm Saturation Breach</td>
<td className="py-2.5 px-3 text-right font-telemetry-data text-primary-container">89.1% [A-]</td>
<td className="py-2.5 px-3 text-on-surface-variant font-mono">0 Critical</td>
<td className="py-2.5 px-3 font-label-sm text-label-sm text-primary-container font-bold">QUAL [EXCELLENT]</td>
<td className="py-2.5 px-3 text-right">
<button className="text-secondary-container hover:underline font-label-sm text-label-sm uppercase font-mono" type="button">
                    [AAR DEBRIEF]
                  </button>
</td>
</tr>
{/*  Log Row 3 (Pass)  */}
<tr className="bg-surface-container-low hover:bg-surface-container transition-colors">
<td className="py-2.5 px-3 font-telemetry-data text-primary">SIM-EX-2025-037</td>
<td className="py-2.5 px-3 font-mono text-on-surface-variant">2025-10-11</td>
<td className="py-2.5 px-3 font-medium text-on-surface">EW Jamming &amp; Low AGL Ingress</td>
<td className="py-2.5 px-3 text-right font-telemetry-data text-primary">85.6% [B+]</td>
<td className="py-2.5 px-3 text-on-surface-variant font-mono">0 Critical</td>
<td className="py-2.5 px-3 font-label-sm text-label-sm text-primary font-bold">QUALIFIED</td>
<td className="py-2.5 px-3 text-right">
<button className="text-secondary-container hover:underline font-label-sm text-label-sm uppercase font-mono" type="button">
                    [AAR DEBRIEF]
                  </button>
</td>
</tr>
{/*  Log Row 4 (Provisional)  */}
<tr className="bg-surface hover:bg-surface-container transition-colors">
<td className="py-2.5 px-3 font-telemetry-data text-primary">SIM-EX-2025-029</td>
<td className="py-2.5 px-3 font-mono text-on-surface-variant">2025-10-02</td>
<td className="py-2.5 px-3 font-medium text-on-surface">High-Altitude Hypersonic Recon</td>
<td className="py-2.5 px-3 text-right font-telemetry-data text-on-surface-variant">79.0% [C+]</td>
<td className="py-2.5 px-3">
<span className="px-1 py-0.5 bg-surface-container-highest border border-outline text-on-surface-variant font-label-sm text-[9px]">
                    1 KINETIC LEAK
                  </span>
</td>
<td className="py-2.5 px-3 font-label-sm text-label-sm text-secondary font-bold">PROVISIONAL</td>
<td className="py-2.5 px-3 text-right">
<button className="text-secondary-container hover:underline font-label-sm text-label-sm uppercase font-mono" type="button">
                    [AAR DEBRIEF]
                  </button>
</td>
</tr>
</tbody>
</table>
</div>
</div>
{/*  SECTION 4: REMEDIATION & CERTIFICATION PATHWAY (BOTTOM WORKBENCH)  */}
<div className="p-space-md bg-surface-container-lowest flex flex-col gap-space-md">
<div className="flex items-center justify-between border-b border-outline-variant pb-space-xs">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-tertiary-fixed-dim">verified_user</span>
<span className="font-label-md text-label-md text-primary uppercase font-bold tracking-wide">
              REMEDIATION DIRECTIVE &amp; CERTIFICATION PIPELINE
            </span>
</div>
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase">EVALUATOR: MAJ. H. VANCE [TAC-01]</span>
</div>
<div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
{/*  Assigned Directive Box  */}
<div className="lg:col-span-6 bg-surface-container p-space-sm border-l-4 border-tertiary-fixed-dim flex flex-col justify-between">
<div className="flex flex-col gap-1">
<div className="flex items-center justify-between">
<span className="font-label-sm text-label-sm text-tertiary-fixed-dim font-bold uppercase tracking-wider">
                  MANDATORY REMEDIATION ASSIGNMENT
                </span>
<span className="font-label-sm text-label-sm text-on-surface-variant font-mono">PRIORITY-1</span>
</div>
<p className="font-headline-sm text-headline-sm text-on-surface font-semibold">
                SIM-EX-2025-052: Advanced Spoofed Beacon Discrimination
              </p>
<p className="font-body-sm text-body-sm text-on-surface-variant">
                Pilot must isolate friendly Mode-4 transponder pings against high-rate adversarial deceptive spoof pulses under simulated 40-target swarm saturation. Focus on saccadic gaze discipline and secondary thermal cross-cue.
              </p>
</div>
<div className="pt-space-sm mt-space-sm border-t border-outline-variant flex items-center justify-between font-label-sm text-label-sm">
<span className="text-on-surface-variant">DEADLINE: 2025-11-02 18:00Z</span>
<span className="text-tertiary-fixed-dim font-bold">EST DURATION: 45 MINS</span>
</div>
</div>
{/*  Milestones Checklist  */}
<div className="lg:col-span-6 bg-surface-container p-space-sm border border-outline-variant flex flex-col justify-between">
<span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
              CR-1 ADVANCEMENT GATES (STANAG 4586 LVL-4)
            </span>
<div className="flex flex-col gap-1.5 mt-1 font-label-sm text-label-sm">
<div className="flex items-center gap-2 text-primary-container">
<span className="material-symbols-outlined text-[16px]">check_box</span>
<span className="text-on-surface">Basic Polar C2 Intercept Operations <span className="text-on-surface-variant font-mono text-[9px]">(Cert: 2025-08-12)</span></span>
</div>
<div className="flex items-center gap-2 text-primary-container">
<span className="material-symbols-outlined text-[16px]">check_box</span>
<span className="text-on-surface">High-Density Swarm Kinetic Allocation <span className="text-on-surface-variant font-mono text-[9px]">(Cert: 2025-09-04)</span></span>
</div>
<div className="flex items-center gap-2 text-tertiary-fixed-dim">
<span className="material-symbols-outlined text-[16px]">check_box_outline_blank</span>
<span className="font-bold">Mode-4 Anti-Spoof Discrimination <span className="text-tertiary-fixed-dim font-mono text-[9px]">[PENDING RE-TEST]</span></span>
</div>
<div className="flex items-center gap-2 text-outline">
<span className="material-symbols-outlined text-[16px]">lock</span>
<span>Night/Zero-Vis Thermal Threat Intercept <span className="text-outline font-mono text-[9px]">[LOCKED]</span></span>
</div>
</div>
</div>
</div>
{/*  Terminal Command Action Bar  */}
<div className="flex flex-wrap items-center justify-between gap-space-sm pt-space-xs border-t border-outline-variant">
<div className="flex items-center gap-space-xs">
<button className="px-space-md py-1.5 bg-primary-container text-on-primary font-label-md text-label-md font-bold hover:brightness-110 transition-all uppercase flex items-center gap-1.5 shadow-[0_0_10px_rgba(0,255,102,0.35)]" type="button">
<span className="material-symbols-outlined text-[18px]">play_arrow</span>
<span>LAUNCH REMEDIATION SIM [SIM-EX-052]</span>
</button>
<button className="px-space-sm py-1.5 bg-surface-container border border-outline-variant font-label-sm text-label-sm text-on-surface hover:bg-surface-container-high transition-colors uppercase flex items-center gap-1" type="button">
<span className="material-symbols-outlined text-[16px] text-secondary-container">print</span>
<span>PRINT QUAL CERT</span>
</button>
</div>
<button className="px-space-sm py-1.5 bg-transparent border border-error/60 text-error hover:bg-error hover:text-on-error transition-all font-label-sm text-label-sm uppercase flex items-center gap-1" type="button">
<span className="material-symbols-outlined text-[16px]">admin_panel_settings</span>
<span>OVERRIDE READINESS STATUS</span>
</button>
</div>
</div>
</section>
</div>
</div></main></div>
    </div>
  );
}
