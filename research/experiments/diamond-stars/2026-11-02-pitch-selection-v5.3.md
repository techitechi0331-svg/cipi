# DIAMOND STARS 3D — Pitch Selection Workflow v5.3
Date: 2026-11-02 (Asia/Tokyo)

## Record type
- Track: original baseball game; Windows standalone launcher (product artifact outside CIPI).
- Evidence classification: SOURCE_FACT (requested behavior), MEASURED (headless browser UI tests and binary self-test), UNVERIFIED (Windows native launch).
- CIPI role: research/evidence and handoff record only. Product code and binary are **not** stored or promoted through CIPI.
- Approval: pending human Windows playtest; no autonomous product promotion.

## Decision
Change pitching from mouse aim + Space twice to a strict three-step flow:
1. Pitch type: five onscreen buttons or keyboard 1–5. Straight 154 km/h, curve 114, slider 138, fork 128, changeup 108.
2. Pitch location: select one cell of a visible 5×5 grid. Interior 3×3 cells are strikes; outer perimeter cells are balls. The selection is locked before release, with a small accuracy variation retained.
3. Release: Space or the 投球する button. Cannot throw before selecting both type and location. Both selections can be revised.

Preserves CPU batting, shrinking ring timing, manual fielding/throws, and pitcher-to-plate ball direction.

## Verification (2026-11-02)
- Headless Chromium viewports 1280, 594, 390 pixels: all passed.
- Defensive phase presents five pitch buttons, throw disabled.
- Choosing pitch index 3 (fork) opens 25 location buttons.
- Choosing row 1, column 3 targets x=0.85, y=0.15 and unlocks release.
- Space starts the ball with pitch type 3, near the selected target. Location panel hides.
- No uncaught JavaScript errors in the tested viewports.
- Go standalone launcher embedded-HTML self-test PASS.
- Windows PE32+ amd64 GUI binary successfully compiled.
- Not verified: Windows native launch of v5.3, long-game regression, user acceptance on live Windows machine.

## Immutable artifact hashes (SHA-256)
- DIAMOND_STARS_3D_v5_3.html: b13c9c815c33d79a63a7a5f4aad11f9cb8bd0a2f3a7fdddfe6f833aaf98c4e14
- DIAMOND_STARS_3D_Windows_v5_3.exe: b11835a576894661d440def68897dc46411b649eb5dc6122ba693d48a58f7b8e

## Human gate / Next steps
- User to launch the v5.3 EXE on Windows and verify pitch type → target → release, directional flight, hitting, and defense.
- Failed observations should become new evidence; do not mark Windows validation complete without user confirmation.


## Loader recovery v5.3.1 (2026-11-02)
- User reported that v5.3 **could not be loaded** (exact error screen is not available).
- The v5.3 HTML itself passed rerun browser logic tests. Root cause in the user's environment remains **unconfirmed**.
- Replacement Windows launcher no longer opens a temporary localhost HTTP server. It extracts the bundled HTML to %LOCALAPPDATA%/DiamondStars/Standalone and opens that local HTML in Edge/Chrome app mode.
- Linux-side launcher extraction and browser invocation tests passed.
- Embedded game extracted bytes SHA-256: 676c12a8d75099a8b7d615dc90f9948668413fcf9df067354631d0d3a3783e60
- Windows x64 PE executable SHA-256: 510585f053fe67a4d2025ec834f2b94897cc766bc38b0f66f3be90f53e19fac7
- Browser execution tests of the v5.3.1 HTML at 1280/594/390 widths passed pitch selection → course selection → Space release with zero uncaught JS errors.
- Limitations: this test environment restricts browser navigation to file://, so the precise local-file launch cannot be verified in Chromium here; Windows user confirmation remains necessary.
- Status: proposed fix, not yet accepted or validated on the user's Windows PC; no main branch promotion.
