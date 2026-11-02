# Benchmark: Wangan Midnight Maximum Tune 6RR PLUS vs MIDNIGHT HIGHWAY v0.5.9
Date: 2026-11-02. Research-only comparator, **not a code change** or a reverse-engineered copy. Information below distinguishes official published behavior from source-code observations and proposed design directions.

## Product positioning
- **WMMT6RR PLUS** is the currently operating Japanese arcade installment according to official 2026-07-10 announcement; **IGNITION** remains in development/2026-11-06–07 expo demo phase, and announces upcoming story 30 episodes, team 2on2, four initial routes.
- WMMT6RR PLUS: high-speed arcade experience, 300km/h+; real licensed cars; large steering + six-speed H-gate gearshift (AT optional); power/handling progress; story/versus/ghost/time attack; persistence/rank/collectibles.
- **Original MIDNIGHT HIGHWAY target**: Assetto-like physical coherence + Wangan-like fun and battling + touge/Initial D style drifting. Avoid trademarked assets/official text/music/vehicle licensing claims in the game.

## Official factual benchmarks

| Feature | WMMT6RR PLUS official | MIDNIGHT HIGHWAY v0.5.9 source | Gap / candidate remedy |
| --- | --- | --- | --- |
| High-speed feeling | Official 300km/h+ arcade racing | 3 fictional vehicles, scripted numeric top-speed/acceleration and speed-dependent FOV | Physical driver feedback, scenery rhythm, boost atmosphere without artificial speed locks |
| Cars and gearbox | 13 brands, >100 models, 6-speed manual or AT | 3 fictional models; gear/RPM calculated from km/h via `Math.floor(km/49)+1`, no driveline/real shift | Torque curve, gears, differential, shift logic, AT/MT, vehicle distinctness |
| Tuning | 100 story episodes; tune reaches 600 hp by ep 20, 800 by ep 50, 840 by ep 80; power/handling setup before race after ep 21 | Engine/tires/suspension stage 0..2 and short/normal/long ratio, no campaign progression/unlock economy | Progression rewards + physical tuning as separate systems |
| Routes | Wangan east 23.7km / three lanes; Hakone outward 8.5km; Taikanzan uphill 12.1km; extensive expressways and free branching | Wangan ~6.65km four lanes, sinusoidal xy centerline; touge ~3.6km, 7 near-equal 58m switchbacks | Route variety, recognizable sections, road banking, landmark/tunnel/junction detail, wider high speed segments where suitable |
| Driving physics | Official marketing says arcade exhilarating handling; exact tire/steering equations not publicly disclosed | Simplified single-track/yaw control, smoothed handbrake slip, planar lateral speed, geometric `recoverCoordinates` projection; no 4-wheel suspension or force model | More coherent lateral dynamics, grip/slip/weight transfer, smooth keyboard response, validated drift release |
| Race opponents | Real player 4-up, 1st place chooses junction; ghost reproduces past player driving lines and may collide | AI rival follows preassigned lane and target speed from curvature; traffic moves by distance/constant lane | AI steering/collision/traffic-aware path planning, 1v1 pacing, ghost replay |
| UI & rewards | Race rankings, title, ghost stamp, versus stars, dress-up level, tuning unlocks | Distance/score/mini map, drift combo, time bests in localStorage, no persistent career | More compelling battle HUD, campaign/save/medals/replay |
| Visuals/audio | City landmarks/bridges/tunnels; night day, car lighting; selectable original Wangan trance BGM | Single HTML WebGL procedural boxes/trees, simple engine oscillator, basic geometry | Proper materials/meshes/lighting/headlights/taillights, original properly licensed music and SFX |
| Modes | Story (100 ep), local VS 4, ghost, time attack, bingo | Free, time, simple one-rival race | Original campaign chapter arc, ghost/AI races and optional future multiplayer |

## Most critical observations in actual v0.5.9 source (read directly in session)
- `physics()`: steering `deltaMax` declines with velocity, `state.steer` rate-limited; forward drive from static `stats.accel`, velocity/yaw and lateral velocity approximated; handbrake `handSlip` released over ~0.65s; no automatic corner brake by design.
- `makeCourse('wangan')`: x = 35sin(z/420)+20sin(z/1100+.4), z 0..6650 step 8, no real road network; 4 lanes.
- `makeCourse('touge')`: rows of ±220m straight traverses with R=58m semicircular switchbacks. Difficult to offer diverse hairpin, sweepers, S-turns and sightline pacing.
- `makeRival`: a single fixed lane; `physics()` updates rival speed using curvature-based target and `rival.s += rival.v*dt`, no observable lane changes/overtaking plan.
- `updateHUD`: gear and rpm based only on vehicle speed (one step per 49km/h), unlike actual engine speed/transmission state.
- `drawVehicle`: box/quad-based static coupe; no independently animated tire rotation, suspension, real brake light/material/lighting.
- `localStorage`: saves options and best run time; limited progression.
- `Canvas2D` fallback is painter-sorted 3D projection, not faithful hardware depth test; should be treated as compatibility mode.

## Priority work plan: not a completed fix
- **P0 PLAYABILITY**: instrument actual 50/70/100/150/250 km/h keyboard + controller steering; avoid forced auto brake/lane center; make countersteer and handbrake transitions predictable; course corner radius vs traction envelope matrix. Human feedback is a release gate.
- **P0 ENGINE/TRACK**: separate 3D world coordinates, route graph and vehicle motion/collisions (stop relying on nearest centerline arc-length projection to drive world motion). Add three deliberate test circuits with telemetry.
- **P1 WANGAN CORE**: 1v1 race with coherent opponent paths and slipstream, recognizable skyline/tunnels/bridge/traffic, readable gap HUD, pressure/finish presentation. Make small but polished vertical slice first.
- **P1 CAR FEEDBACK**: actual gearing and RPM, torque/differential, engine braking, sound states, brake and shift feel; visual tire/suspension reaction; keep arcade preset separate from sim preset.
- **P2 GROWTH**: save slot, stage progression, unlockables, ghost run recording/playback, time leaderboard (local initially), distinct cosmetic-only dress-up and performance tuning.
- **P2 DEPLOYMENT**: fully tested Windows launcher/updater, controlled private code releases and reproducible tests.

## Official sources (URLs)
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/story/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/vsplayer/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/ghost/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/timeattack/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/course/wangan1.html
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/course/hakone1.html
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/system/course/taikan1.html
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/faq/
- https://wanganmaxi-official.com/wanganmaxi6rrplus/jp/bgm/
- https://bandainamco-am.co.jp/am/vg/wmsi/jp/news/20260710/
- https://bandainamco-am.co.jp/am/vg/wmsi/jp/amexpo2026/

## Evidence quality and boundaries
- Published official game content = authoritative for feature descriptions, not proprietary implementation equations.
- MIDNIGHT HIGHWAY code references = direct source inspection of v0.5.9 in the active conversation container; no evidence of an authorized game-source repo. Do not copy trademarked names, artwork or original BGM into distributable original game without licenses.
- This document does not prove WMMT's unseen physics engine or that user-playability issues are solved. Remains an unmerged draft PR with human review.
