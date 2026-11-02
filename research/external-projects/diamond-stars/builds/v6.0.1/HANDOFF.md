# DIAMOND STARS 3D v6.0.1 — Defensive Camera / Fielding Hotfix

**Date:** 2026-11-02 (Asia/Tokyo)
**Product:** Original baseball game (not affiliated with Konami).
**Scope:** v6.0 defensive-view/hit-balance regression repair. Draft for human acceptance.

## Authoritative CIPI artifact
- Exact v6.0.1 HTML source: `research/external-projects/diamond-stars/builds/v6.0.1/DIAMOND_STARS_3D_v6_0_1.html`
- This handoff: `research/external-projects/diamond-stars/builds/v6.0.1/HANDOFF.md`
- Prior v6.0 full-source snapshot/research: PR #457 (not merged as of record).
- EXE and ZIP binaries are distributed separately as conversation deliverables; **binary bytes are not in CIPI**.

## Requested bugs
1. Third base appears as first base due to mirrored field camera.
2. Fielders accelerate and move too fast, making hits difficult.
3. The whole 3D field is clipped in narrower views.
4. Bases are invisible or obscured.

## Implemented fixes
- Restored camera handedness (`D3.right = cross([0,1,0], D3.forward)`). Onscreen 1B (x=+22) is to the RIGHT of 3B (x=-22) at every tested viewport.
- Reduced authored fielder top speed: `2.7 + 0.03 × speedRating` (speed 40→3.9; 90→5.4 in simulation world units/sec). Prior v6: `4.1+0.045×speedRating` (40→5.9; 90→8.15). **Not an official PowerPro formula.**
- Reduced authored acceleration to `2.1 + 0.014×speedRating`; slower initial reaction/pickup/CPU throw; CPU chases with only two nearest defenders, versus three previously.
- Slightly decreased average batter-to-first run time to improve hit/out balance; subjective balance requires real gameplay validation.
- Moved the field camera farther back with focus scaled on mid-width windows; 594px view home plate vertical screen coordinate 357.8 within game canvas height 435.
- Grass render covers the previously uncovered foreground.
- Added a prominent overlay of 1B, 2B, 3B and HOME base diamonds after player rendering to prevent accidental occlusion.
- Slimmed top and bottom HUD panels where possible.

## Verification
- `node --check` JavaScript syntax PASS.
- Chromium `page.set_content` + live simulation tested viewport widths 1280×900, 594×900, 390×840, all with 0 uncaught JavaScript errors.
- All 3 viewport tests: 9 defenders, field rendering, 1B screen.x > 3B screen.x, home below infield and above bottom HUD (check threshold: home screen.y < canvas height - 40); screenshot captures rendered locally.
- At 594px: first base x=422.49, third base x=157.51, home y=357.83 vs canvas h=435.
- Go Linux launcher built and ran `DIAMOND_TEST_EXTRACT=1 ./linux_launcher --self-test` successfully; SHA-256-verified extracted HTML.
- Windows PE32+ x86-64 GUI executable built; ZIP archive integrity test passed.
- GitHub content blob SHA exactly matched `git hash-object` of local source: `cab024a96246e7e8149526ccb8e550bfdc38aef4`.

## Release fingerprints
- HTML SHA-256: `0b90ea3ab8c1d5d9645628b3c211a0ae4d6cac54bee62ab68f1345ec6276fec1`
- Windows EXE SHA-256: `865a91922d9ad1b3093e94560da43ecb6da411a1978614c7c49695cfb988fdc8`
- Windows ZIP SHA-256: `502ea0e55165310e411091dc1c53b97951196bc0141ea8c2ca13b8b00db99314`
- Go gameFilename: `diamond-stars-3d-v6.0.1.html`
- Launcher extracts it to `%LOCALAPPDATA%/DiamondStars/Standalone/` and opens it in Edge/Chrome app mode (no localhost server).

## Limitations / human approval required
- Windows v6.0.1 native launch **not confirmed** on the user's device as of this record.
- Hit frequency was not statistically calibrated across thousands of plays; no claim that baseball balance is final.
- 3D rendering is perspective-projected CPU software 3D, not skeletal-animated GPU 3D.
- Out/force/runner logic remains a simplification of full baseball rules.
- UI is more readable in checked viewports but may need further polish in real Windows window scaling.
- This is a PUBLIC research branch in the CIPI repository; the original source file is public.
- Do not merge to main or mark final until human review.

## Next gate
1. Windows PC: user launches new EXE; confirms orientation, 4 visible bases, fielder pace, and hit/out feel.
2. Quantitative balance pass: at least 1000 representative grounders/flies per difficulty, fielders at different ability scores, evaluate hit/outs and batted-ball spread.
3. Simulated baserunning, player catching/throwing and camera follow refinement after feedback.
4. For every subsequent release: archive exact source (Git blob SHA checked), EXE fingerprint, QA matrix and human-gate status to CIPI as a separate draft PR.
