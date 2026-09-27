from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

def run(cmd, cwd: Path | None = None, capture: bool = False) -> str:
    print("+", " ".join(map(str, cmd)))
    result = subprocess.run(
        [str(x) for x in cmd],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=capture,
        check=False,
    )
    if capture:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(map(str, cmd))}")
    return result.stdout if capture else ""

def configure(source: Path, build: Path, *defs: str) -> None:
    cmd = ["cmake", "-S", source, "-B", build, "-G", "Visual Studio 17 2022", "-A", "x64"]
    cmd.extend(defs)
    run(cmd)

def build(path: Path) -> None:
    run(["cmake", "--build", path, "--config", "Release", "--parallel"])

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def pick(rows: list[dict[str, str]], *, scope: str, frequency: float, level: float, mode: str = "NA", pr: float = 0.0) -> dict[str, str]:
    for row in rows:
        if (
            row["scope"] == scope
            and abs(float(row["frequency_hz"]) - frequency) < 0.01
            and abs(float(row["input_dbfs"]) - level) < 0.01
            and row["mode"] == mode
            and abs(float(row["peak_reduction"]) - pr) < 0.01
        ):
            return row
    raise RuntimeError(f"row missing: {scope=} {frequency=} {level=} {mode=} {pr=}")

def write_gate(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")

def patch_direct_gain(engine_dir: Path) -> None:
    path = engine_dir / "LA2AEngine.cpp"
    text = path.read_text(encoding="utf-8")
    old1 = "    const auto n = juce::jlimit(0.0f, 1.0f, params.gain / 100.0f);"
    old2 = "    return dbToGain(-18.0f + 36.0f * std::pow(n, 0.82f));"
    new1 = "    const auto gainDb = juce::jlimit(-18.0f, 18.0f, params.gain);"
    new2 = "    return dbToGain(gainDb);"
    if old1 not in text or old2 not in text:
        if new1 in text and new2 in text:
            return
        raise RuntimeError(f"Gain mapping anchor missing: {path}")
    text = text.replace(old1, new1, 1).replace(old2, new2, 1)
    path.write_text(text, encoding="utf-8")

def compiled_isolation(root: Path, juce: Path, results: Path) -> dict:
    patch_direct_gain(root / "prehost-baseline-engine")
    patch_direct_gain(root / "prehost-candidate-engine")
    lab = root / "Research" / "17_PreHostHA100X"
    build_dir = root / "build-prehost-probe"
    configure(
        lab,
        build_dir,
        f"-DJUCE_PATH={juce}",
        f"-DBASELINE_ENGINE_DIR={root / 'prehost-baseline-engine'}",
        f"-DCANDIDATE_ENGINE_DIR={root / 'prehost-candidate-engine'}",
    )
    build(build_dir)

    out = results / "isolation"
    out.mkdir(parents=True, exist_ok=True)
    base_csv = out / "baseline.csv"
    cand_csv = out / "candidate.csv"
    run([build_dir / "vl2a_prehost_baseline_artefacts" / "Release" / "vl2a_prehost_baseline.exe", base_csv])
    run([build_dir / "vl2a_prehost_candidate_artefacts" / "Release" / "vl2a_prehost_candidate.exe", cand_csv])

    base = read_csv(base_csv)
    cand = read_csv(cand_csv)
    if any(row["finite"] != "1" for row in base + cand):
        raise RuntimeError("compiled isolation produced non-finite data")

    b1 = pick(base, scope="transformer", frequency=1000, level=-18)
    if not 0.008 <= float(b1["thd_pct"]) <= 0.015:
        raise RuntimeError("baseline transformer THD provenance mismatch")
    if not 0.14 <= float(b1["gain_db"]) <= 0.18:
        raise RuntimeError("baseline transformer gain provenance mismatch")

    c30 = pick(cand, scope="transformer", frequency=30, level=-48)
    c1 = pick(cand, scope="transformer", frequency=1000, level=-48)
    c20 = pick(cand, scope="transformer", frequency=20000, level=-48)
    rel30 = float(c30["gain_db"]) - float(c1["gain_db"])
    rel20 = float(c20["gain_db"]) - float(c1["gain_db"])
    if abs(rel30) > 0.10:
        raise RuntimeError(f"candidate 30 Hz relative response outside gate: {rel30}")
    if abs(rel20) > 0.10:
        raise RuntimeError(f"candidate 20 kHz relative response outside gate: {rel20}")
    if float(c1["thd_pct"]) > 0.001:
        raise RuntimeError(f"linear candidate unexpectedly nonlinear: {c1['thd_pct']}")

    bc = pick(base, scope="engine", frequency=1000, level=-18, mode="COMP", pr=50)
    cc = pick(cand, scope="engine", frequency=1000, level=-18, mode="COMP", pr=50)
    bl = pick(base, scope="engine", frequency=1000, level=-18, mode="LIMIT", pr=50)
    cl = pick(cand, scope="engine", frequency=1000, level=-18, mode="LIMIT", pr=50)
    comp_delta = float(cc["final_gr_db"]) - float(bc["final_gr_db"])
    limit_delta = float(cl["final_gr_db"]) - float(bl["final_gr_db"])
    if abs(comp_delta) > 1.5:
        raise RuntimeError(f"COMP PR50 regression too large: {comp_delta}")
    if abs(limit_delta) > 1.5:
        raise RuntimeError(f"LIMIT PR50 regression too large: {limit_delta}")

    metrics = {
        "candidate_30Hz_rel_1k_db": rel30,
        "candidate_20kHz_rel_1k_db": rel20,
        "candidate_transformer_thd_pct": float(c1["thd_pct"]),
        "comp_pr50_delta_db": comp_delta,
        "limit_pr50_delta_db": limit_delta,
    }
    write_gate(out / "ISOLATION_GATE.txt", [
        "CLASSIFICATION=MEASURED_COMPILED_RESEARCH",
        "AUTOMATIC_PRODUCT_DECISION=false",
        *(f"{k}={v}" for k, v in metrics.items()),
        "RESULT=PASS",
    ])
    return metrics

def control_regression(root: Path, juce: Path, results: Path) -> dict:
    build_dir = root / "build-prehost-control"
    configure(
        root / "Research" / "09_FinalValidation",
        build_dir,
        f"-DJUCE_PATH={juce}",
        f"-DENGINE_DIR={root / 'prehost-candidate-engine'}",
    )
    build(build_dir)
    out = results / "control"
    out.mkdir(parents=True, exist_ok=True)
    run([build_dir / "vl2a_final_control_regression_artefacts" / "Release" / "vl2a_final_control_regression.exe", out])

    rows = read_csv(out / "matched_release.csv")
    if not rows:
        raise RuntimeError("matched_release.csv empty")
    row = rows[0]
    retention = float(row["retained_60ms"])
    start = float(row["start_gr_db"])
    if not 0.47 <= retention <= 0.55:
        raise RuntimeError(f"60 ms release retention regression: {retention}")
    if not 5.0 <= start <= 6.6:
        raise RuntimeError(f"matched release start GR regression: {start}")

    sr = read_csv(out / "sample_rate.csv")
    values = [float(r["final_gr_db"]) for r in sr]
    spread = max(values) - min(values)
    if spread >= 0.20:
        raise RuntimeError(f"sample-rate GR spread regression: {spread}")
    write_gate(out / "CONTROL_GATE.txt", [
        f"matched_release_start_gr_db={start}",
        f"matched_release_retained_60ms={retention}",
        f"sample_rate_gr_spread_db={spread}",
        "RESULT=PASS",
    ])
    return {"start_gr_db": start, "retained_60ms": retention, "sample_rate_spread_db": spread}

def state_compatibility(root: Path, juce: Path, results: Path) -> None:
    build_dir = root / "build-state-compat"
    configure(root / "Research" / "15_StateCompatibility", build_dir, f"-DJUCE_PATH={juce}")
    build(build_dir)
    exe = build_dir / "vl2a_state_compatibility_artefacts" / "Release" / "vl2a_state_compatibility.exe"
    text = run([exe], capture=True)
    out = results / "state"
    out.mkdir(parents=True, exist_ok=True)
    (out / "equivalence.txt").write_text(text + "\nRESULT=PASS\n", encoding="utf-8")

def download_vocals(root: Path) -> dict[str, Path]:
    out = root / "vocal_inputs"
    out.mkdir(parents=True, exist_ok=True)
    base = "https://huggingface.co/datasets/stemsai/vocalset/resolve/9763b3439b6034b797a6f2cd8118b8842a430c2f/VocalSet/FULL/female3"
    urls = {
        "breathy": f"{base}/arpeggios/breathy/f3_arpeggios_breathy_a.wav?download=true",
        "straight": f"{base}/excerpts/straight/f3_caro_straight.wav?download=true",
        "forte": f"{base}/long_tones/forte/f3_long_forte_a.wav?download=true",
    }
    paths = {}
    for name, url in urls.items():
        target = out / f"{name}.wav"
        if not target.exists() or target.stat().st_size < 10000:
            print("download", url)
            urllib.request.urlretrieve(url, target)
        paths[name] = target
    return paths

def real_vocal(root: Path, juce: Path, results: Path) -> dict:
    base_build = root / "build-ab-baseline"
    cand_build = root / "build-ab-candidate"
    analyzer_build = root / "build-ab-analyzer"
    configure(
        root / "Research" / "09_FinalValidation" / "AB",
        base_build,
        f"-DJUCE_PATH={juce}",
        f"-DENGINE_DIR={root / 'prehost-baseline-engine'}",
        "-DTARGET_NAME=vl2a_prehost_ab_baseline",
    )
    configure(
        root / "Research" / "09_FinalValidation" / "AB",
        cand_build,
        f"-DJUCE_PATH={juce}",
        f"-DENGINE_DIR={root / 'prehost-candidate-engine'}",
        "-DTARGET_NAME=vl2a_prehost_ab_candidate",
    )
    configure(
        root / "Research" / "09_FinalValidation" / "Analyzer",
        analyzer_build,
        f"-DJUCE_PATH={juce}",
    )
    build(base_build)
    build(cand_build)
    build(analyzer_build)

    baseline = base_build / "vl2a_prehost_ab_baseline_artefacts" / "Release" / "vl2a_prehost_ab_baseline.exe"
    candidate = cand_build / "vl2a_prehost_ab_candidate_artefacts" / "Release" / "vl2a_prehost_ab_candidate.exe"
    analyzer = analyzer_build / "vl2a_ab_analyzer_artefacts" / "Release" / "vl2a_ab_analyzer.exe"
    inputs = download_vocals(root)

    audio = results / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    rows = []
    grs = []
    for name, inp in inputs.items():
        a = audio / f"{name}-baseline.wav"
        b = audio / f"{name}-candidate.wav"
        run([baseline, inp, a, "50", "0", "Compress", "512", "-18"], capture=True)
        cand_line = run([candidate, inp, b, "50", "0", "Compress", "512", "-18"], capture=True).strip().splitlines()[-1]
        parts = cand_line.split(",")
        if len(parts) < 12:
            raise RuntimeError(f"unexpected candidate renderer output: {cand_line}")
        max_gr = float(parts[11])
        grs.append(max_gr)

        metric_line = run([analyzer, a, b], capture=True).strip().splitlines()[-1]
        metrics = [float(x) for x in metric_line.split(",")]
        if len(metrics) < 6:
            raise RuntimeError(f"unexpected A/B analyzer output: {metric_line}")
        match_db, corr, residual_db, derivative_delta_db, centroid_shift_pct, max_band = metrics[:6]
        if corr < 0.985:
            raise RuntimeError(f"candidate correlation safety gate failed: {name} {corr}")
        if abs(derivative_delta_db) > 0.75:
            raise RuntimeError(f"candidate transient safety gate failed: {name} {derivative_delta_db}")
        if max_band > 1.0:
            raise RuntimeError(f"candidate spectral safety gate failed: {name} {max_band}")
        rows.append({
            "clip": name,
            "candidate_max_gr_db": max_gr,
            "match_db": match_db,
            "correlation": corr,
            "residual_db": residual_db,
            "derivative_delta_db": derivative_delta_db,
            "centroid_shift_pct": centroid_shift_pct,
            "max_abs_band_shift_db": max_band,
        })

    sorted_gr = sorted(grs)
    median_gr = sorted_gr[1]
    if not 5.0 <= median_gr <= 7.0:
        raise RuntimeError(f"candidate PR50 median outside 5..7 dB: {median_gr}")
    if sorted_gr[0] < 4.0 or sorted_gr[-1] > 8.5:
        raise RuntimeError("candidate PR50 per-clip spread outside 4..8.5 dB")

    with (results / "vocal_metrics.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_gate(results / "VOCAL_GATE.txt", [f"median_max_gr_db={median_gr}", "RESULT=PASS"])
    return {"median_max_gr_db": median_gr, "clips": rows}

def performance(root: Path, juce: Path, results: Path) -> dict:
    build_dir = root / "build-prehost-perf"
    configure(
        root / "Research" / "09_FinalValidation" / "Latency",
        build_dir,
        f"-DJUCE_PATH={juce}",
        f"-DENGINE_DIR={root / 'prehost-candidate-engine'}",
    )
    build(build_dir)
    out = results / "perf"
    out.mkdir(parents=True, exist_ok=True)
    cpu_text = run([build_dir / "vl2a_cpu_probe_artefacts" / "Release" / "vl2a_cpu_probe.exe"], capture=True)
    latency_text = run([build_dir / "vl2a_latency_probe_artefacts" / "Release" / "vl2a_latency_probe.exe"], capture=True)
    (out / "cpu.txt").write_text(cpu_text, encoding="utf-8")
    (out / "latency.txt").write_text(latency_text, encoding="utf-8")

    cpu_values = []
    for line in cpu_text.splitlines():
        for part in line.split(","):
            if part.startswith("single_core_realtime_pct="):
                cpu_values.append(float(part.split("=", 1)[1]))
    if not cpu_values:
        raise RuntimeError("CPU probe emitted no realtime percentages")
    worst = max(cpu_values)
    if not math.isfinite(worst) or worst > 12.0:
        raise RuntimeError(f"pre-host CPU safety gate failed: {worst}%")
    return {"worst_single_core_realtime_pct": worst}

def prepare_product_source(root: Path, juce: Path) -> Path:
    archive_b64 = root / "vl2a_project.tar.gz.b64"
    raw = "".join(archive_b64.read_text(encoding="utf-8").split())
    archive = root / "vl2a_project.tar.gz"
    archive.write_bytes(base64.b64decode(raw))

    product = root / "VocalLeveler2A"
    if product.exists():
        shutil.rmtree(product)
    product.mkdir()
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(product)

    source = root / "vl2a_lineamp_v01" / "Source"
    for name in ("LA2AEngine.cpp", "LA2AEngine.h", "LineAmplifierDSP.h", "HA100XPreHostModel.h"):
        shutil.copy2(source / name, product / "Source" / name)
    for name in ("PluginEditor.cpp", "PluginEditor.h"):
        shutil.copy2(root / "vl2a_white_ui_code" / "Source" / name, product / "Source" / name)

    peak_script = root / "Research" / "08_RC2" / "apply_processor_peak_hold.ps1"
    run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", peak_script, product / "Source"])

    pp = product / "Source" / "PluginProcessor.cpp"
    ep = product / "Source" / "LA2AEngine.cpp"
    cp = product / "CMakeLists.txt"

    text = pp.read_text(encoding="utf-8")
    old = "juce::NormalisableRange<float>(0.0f, 100.0f, 0.01f, 0.75f), 45.0f));"
    new = "juce::NormalisableRange<float>(-18.0f, 18.0f, 0.01f), 0.0f));"
    if old not in text:
        raise RuntimeError("legacy Gain parameter anchor missing")
    pp.write_text(text.replace(old, new, 1), encoding="utf-8")

    text = ep.read_text(encoding="utf-8")
    old1 = "    const auto n = juce::jlimit(0.0f, 1.0f, params.gain / 100.0f);"
    old2 = "    return dbToGain(-18.0f + 36.0f * std::pow(n, 0.82f));"
    if old1 not in text or old2 not in text:
        raise RuntimeError("legacy Gain DSP anchor missing")
    text = text.replace(old1, "    const auto gainDb = juce::jlimit(-18.0f, 18.0f, params.gain);", 1)
    text = text.replace(old2, "    return dbToGain(gainDb);", 1)
    ep.write_text(text, encoding="utf-8")

    text = cp.read_text(encoding="utf-8")
    if 'PRODUCT_NAME "Vocal Leveler 2A"' not in text:
        raise RuntimeError("product-name anchor missing")
    text = text.replace('PRODUCT_NAME "Vocal Leveler 2A"', 'PRODUCT_NAME "VL2A"', 1)
    text = text.replace("project(VocalLeveler2A VERSION 0.3.0", "project(VocalLeveler2A VERSION 0.6.0", 1)
    cp.write_text(text, encoding="utf-8")

    target_juce = product / "JUCE"
    if target_juce.exists():
        if target_juce.is_symlink():
            target_juce.unlink()
        else:
            shutil.rmtree(target_juce)
    run(["cmd", "/c", "mklink", "/J", target_juce, juce])
    return product

def pluginval_and_host(root: Path, juce: Path, results: Path) -> dict:
    product = prepare_product_source(root, juce)
    build_dir = root / "build-prehost-vst3"
    configure(product, build_dir)
    build(build_dir)
    bundle = build_dir / "VocalLeveler2A_artefacts" / "Release" / "VST3" / "VL2A.vst3"
    if not bundle.exists():
        raise RuntimeError("pre-host VST3 bundle missing")

    cache = Path(os.environ.get("RUNNER_TEMP", root / ".tmp")) / "pluginval-1.0.4"
    if cache.exists():
        shutil.rmtree(cache)
    cache.mkdir(parents=True)
    zip_path = cache / "pluginval.zip"
    urllib.request.urlretrieve(
        "https://github.com/Tracktion/pluginval/releases/download/v1.0.4/pluginval_Windows.zip",
        zip_path,
    )
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(cache)
    matches = list(cache.rglob("pluginval.exe"))
    if not matches:
        raise RuntimeError("pluginval.exe missing")
    pluginval = matches[0]
    p = subprocess.run(
        [str(pluginval), "--strictness-level", "10", "--skip-gui-tests", "--timeout-ms", "120000", "--validate", str(bundle)],
        text=True,
        capture_output=True,
        check=False,
    )
    (results / "pluginval-stdout.txt").write_text(p.stdout or "", encoding="utf-8")
    (results / "pluginval-stderr.txt").write_text(p.stderr or "", encoding="utf-8")
    if p.returncode != 0 or "SUCCESS" not in (p.stdout or "").splitlines():
        raise RuntimeError(f"pluginval strictness 10 failed: {p.returncode}")
    write_gate(results / "PLUGINVAL_GATE.txt", ["RESULT=PASS"])

    host_build = root / "build-prehost-host-latency"
    configure(root / "Research" / "15_VST3HostLatency", host_build, f"-DJUCE_PATH={juce}")
    build(host_build)
    host_exe = host_build / "vl2a_vst3_host_latency_artefacts" / "Release" / "vl2a_vst3_host_latency.exe"
    host_text = run([host_exe, bundle], capture=True)
    host_dir = results / "host"
    host_dir.mkdir(parents=True, exist_ok=True)
    (host_dir / "host_latency.txt").write_text(host_text, encoding="utf-8")
    if "RESULT=PASS" not in host_text.splitlines():
        raise RuntimeError("exact VST3 host latency probe failed")
    return {"bundle": str(bundle), "pluginval": "PASS", "host_latency": "PASS"}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--juce", required=True)
    p.add_argument("--track-id", required=True)
    p.add_argument("--candidate-id", required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--evidence-hash", required=True)
    p.add_argument("--staging-branch", required=True)
    args = p.parse_args()

    root = Path(args.root).resolve()
    juce = Path(args.juce).resolve()
    results = root / "prehost-results"
    results.mkdir(parents=True, exist_ok=True)

    isolation = compiled_isolation(root, juce, results)
    control = control_regression(root, juce, results)
    state_compatibility(root, juce, results)
    vocal = real_vocal(root, juce, results)
    perf = performance(root, juce, results)
    vst3 = pluginval_and_host(root, juce, results)

    summary = {
        "schema_version": "1.0",
        "state": "CUBASE_READY_HUMAN_GATE",
        "classification": "PREHOST_AUTOMATED_VALIDATION_NOT_PRODUCT_ADOPTION",
        "track_id": args.track_id,
        "candidate_id": args.candidate_id,
        "source_ref": args.source_ref,
        "source_evidence_hash": args.evidence_hash,
        "staging_branch": args.staging_branch,
        "compiled_isolation": {"result": "PASS", **isolation},
        "control_regression": {"result": "PASS", **control},
        "state_automation": "PASS",
        "real_vocal_objective_ab": {"result": "PASS", **vocal},
        "performance": {"result": "PASS", **perf},
        "pluginval_strictness_10": vst3["pluginval"],
        "exact_vst3_host_latency": vst3["host_latency"],
        "cubase": {
            "scan": "UNVERIFIED",
            "insert": "UNVERIFIED",
            "playback": "UNVERIFIED",
            "automation": "UNVERIFIED",
            "save_reload": "UNVERIFIED",
            "pdc": "UNVERIFIED",
        },
        "listening_judgment": "UNVERIFIED",
        "product_adoption": "UNVERIFIED",
        "release_decision": "UNVERIFIED",
        "automatic_product_decision": False,
        "automatic_release_decision": False,
    }
    (results / "prehost_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
