# Vocal One-Knob Doubler v0.3 product evidence snapshot

This directory imports **numeric and textual evidence only** from the product repository. No raw vocal recording is stored in CIPI.

## Provenance

- Product: `techitechi0331-svg/Vocal-One-Knob-Doubler`
- Product branch: `v0.3-dev`
- Reviewed head: `4b17a9e573b5b1721aa059cd48865fc47b6d8939`
- Core regression: run 36065649839 — PASS
- Windows VST3 + pluginval strictness 5: run 36065649852 — PASS
- Detector corpus: run 36065630813 — PASS
- Real VocalSet-derived v0.2/v0.3 AB: run 36065631021 — PASS

## Scope

The snapshot exists so CIPI can reproduce a bounded baseline-versus-candidate decision without storing the singing WAV files or reaching into the product repository at worker runtime.

The snapshot is not proof of subjective superiority. The queued job only tests predeclared technical conditions.

## Negative evidence retained

The original fixed Mud detector showed approximately 99–100% strong activation on the five-recording calibration set. That failure is retained explicitly and is part of the autonomous acceptance gate.

## Listening evidence limitation

The target-machine development report preferred v0.2 DOUBLE 20–25% for a歌ってみた lead vocal. Session loudness-match details were not formally logged. It motivated the v0.3 50% calibration target but remains limited-scope listening evidence.
