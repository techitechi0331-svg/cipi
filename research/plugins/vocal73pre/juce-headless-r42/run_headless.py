#!/usr/bin/env python3
"""Build and execute the *real* Vocal73DSP JUCE harness with local sources.

No synthetic fallback, no artifact upload. Exit nonzero unless CSV gate passes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path, help="Local VocalPrepComp/Vocal73Pre directory")
    p.add_argument("--juce", required=True, type=Path, help="Local JUCE 9.0.2 source directory")
    p.add_argument("--build", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--config", default="Release")
    args = p.parse_args()
    src, juce = args.source.resolve(), args.juce.resolve()
    harness = Path(__file__).resolve().parent
    build, out = args.build.resolve(), args.out.resolve()
    for f in (src/"Source/Vocal73DSP.cpp", src/"Source/Vocal73DSP.h",
              juce/"CMakeLists.txt", harness/"CMakeLists.txt", harness/"check_csv.py"):
        if not f.is_file():
            p.error(f"Missing required file: {f}")
    build.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    steps = []
    def run(name, command):
        start = time.monotonic()
        proc = subprocess.run(command, capture_output=True, text=True, errors="replace")
        steps.append(dict(step=name, command=command, returncode=proc.returncode,
                          seconds=round(time.monotonic()-start, 3)))
        (out/f"{name}.log").write_text(proc.stdout+"\n[stderr]\n"+proc.stderr, encoding="utf-8")
        if proc.returncode:
            raise RuntimeError(f"{name} failed (exit {proc.returncode})")
        return proc.stdout
    status, error = "FAILED", None
    try:
        run("configure", ["cmake", "-S", str(harness), "-B", str(build),
                          f"-DVOCAL73_SOURCE_DIR={src}", f"-DFETCHCONTENT_SOURCE_DIR_JUCE={juce}",
                          f"-DCMAKE_BUILD_TYPE={args.config}"])
        run("build", ["cmake", "--build", str(build), "--config", args.config,
                      "--target", "vocal73_headless", "--parallel", "2"])
        candidates = (build/"vocal73_headless", build/"vocal73_headless.exe",
                      build/args.config/"vocal73_headless.exe", build/args.config/"vocal73_headless")
        binary = next((x for x in candidates if x.is_file()), None)
        if binary is None:
            binary = next((x for x in list(build.rglob("vocal73_headless.exe")) +
                           list(build.rglob("vocal73_headless")) if x.is_file()), None)
        if binary is None:
            raise RuntimeError("headless executable not found after build")
        measured = run("measure", [str(binary)])
        (out/"measured.csv").write_text(measured, encoding="utf-8")
        run("check", [sys.executable, str(harness/"check_csv.py"), str(out/"measured.csv")])
        status = "PASS"
    except (OSError, RuntimeError) as exc:
        error = str(exc)
    result = dict(status=status, evidence_kind="ACTUAL_JUCE_DSP_EXECUTION" if status == "PASS"
                  else "ATTEMPT_NO_VALIDATED_AUDIO", platform=platform.platform(),
                  python=sys.version.split()[0], source=str(src), juce=str(juce),
                  steps=steps, error=error)
    if status == "PASS":
        data = (out/"measured.csv").read_bytes()
        result["measured_csv_sha256"] = hashlib.sha256(data).hexdigest()
        result["measured_rows"] = len(data.splitlines())-1
    (out/"run_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n",
                                        encoding="utf-8")
    print(json.dumps(dict(status=status, error=error), ensure_ascii=False))
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
