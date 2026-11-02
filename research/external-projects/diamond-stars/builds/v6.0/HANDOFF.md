# DIAMOND STARS 3D — v6.0 Build, Evidence & Handoff
Date: 2026-11-02 (Asia/Tokyo)
Project: original baseball game. Public-reference research conducted separately; no KONAMI assets or code reproduced.

## Source of truth in this CIPI branch
- Full HTML source: research/external-projects/diamond-stars/builds/v6.0/DIAMOND_STARS_3D_v6_0.html
- Research design specification: research/external-projects/diamond-stars/specs/PAWAPURO_RESEARCH_SPEC_2026.md
- This handoff: research/external-projects/diamond-stars/builds/v6.0/HANDOFF.md

## Shipped artifact identity (SHA-256)
- DIAMOND_STARS_3D_v6_0.html
  fc325ae8089b3600fb7bb25b5b9a88d3d77b279cae5df225d8ae96715a2f6a96
- DIAMOND_STARS_3D_Windows_v6_0.exe
  92044d59e8ef71029548143e8dbba48ba33ae7f46ab717280d6e69082efabb03
- The release EXE embeds that HTML byte-for-byte and extracts it into LOCALAPPDATA/DiamondStars/Standalone/diamond-stars-3d-v6.0.html at launch.
- ZIP contains EXE + standalone HTML + Japanese README. The EXE binary itself is distributed in the ChatGPT artifact, **not committed to CIPI**.

## Implemented in v6.0
1. Three-step pitching: choose one of five pitches → choose one of 25 course cells → Space to release.
2. Deterministic 3D ball trajectory shared by pitching display, batter display, impact ring, and contact judgment.
3. Distinct curve, slider, fork, changeup, straight trajectories plus colored motion trails and labels. Pitcher break ability controls level 1–7.
4. Perspective-based 3D-like baseball field and nine independently instantiated defenders (including catcher).
5. Player-specific field speed max = 4.1 + 0.045 * runSpeed (design approximation, **not an official PowerPro formula**); acceleration = 3.2 + 0.023 * runSpeed.
6. Fielder reaction timer, catching skill and pickup delay; arm strength determines throw travel time.
7. Two teams, 18 fictional players, per-player contact, power, trajectory, baserunning, defense speed, fielding, arm, catch; pitcher velocity, control, stamina, break.
8. Player attribute editor and best-effort localStorage persistence.
9. Mute-free original UI with compact pitch meter above the strike zone, shrinking ring, and keyboard/manual defense.

## Verification / evidence
- JavaScript parser: node --check PASS.
- Headless Chromium, via page.set_content: 1280×900, 594×900, 390×840 passed with **zero uncaught page exceptions**.
- Menu, start, inning-ready, roster editor (8 visible fielder ability controls), change contact 89→99, defense launch, 9 defenders with distinct abilities, select FORK, course row/col, Space pitch, pitchWorld trajectory sampling.
- Same-case example pitchWorld at t=0 starts at z=18 and at t=1 reaches home plate z≈-0.3; pitch type 1/2/3/4 at t=.7 each has distinct x/y.
- Defensive top speed for run=40 -> 5.9 m/s; run=90 -> 8.15 m/s. This is an authored design formula.
- Go Windows build success: PE32+ x86-64 GUI application.
- Go launcher: Linux executable --self-test and extract self-test PASS (embedded HTML SHA verified); ZIP archive integrity PASS.
- Source snapshot uploaded and fetched back through GitHub connector matched character-for-character.

## Known limitations and human gate
- Windows real hardware launch of v6.0 **not yet verified** by user.
- No full multi-runner baserunning, umpire precision, complex force/tag plays, defensive errors in all rule contexts, sports physics-grade motion, deep 3D rigging, player growth, long modes or online multiplayer yet.
- The field camera is a perspective software-3D scene, not a skeletal GPU 3D engine.
- Player editor browser origin governs persistence; browsers blocking localStorage may not retain changes across sessions.
- The gameplay is a v6.0 first milestone, **not full 2026–2027 game equivalence**.
- This GitHub repository is public. The full original HTML game source on this research branch is readable by the public.

## Next development gate
1. User confirms Windows EXE starts and pitch type/course/release works.
2. P0-D: genuine independent multi-runner entities and bases; force/tag/touch/return timestamps; ball-bounce authoritative physics; inning & stats regression.
3. P1: pitcher pitch-list editing, fielding positional aptitude, catching mechanics, stamina and special abilities.
4. P2: 3D animation rigs, replay, sounds, practice modes, deterministic sim replay.
5. Always include source snapshot, SHA-256 release manifest, QA matrix and handoff in CIPI for each new version. Merge to main only with explicit human review.
