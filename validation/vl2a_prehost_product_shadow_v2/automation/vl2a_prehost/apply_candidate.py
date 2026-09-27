from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

REQUIRED = (
    "candidate_id",
    "primary_dcr_ohm",
    "secondary_dcr_ohm",
    "magnetizing_h",
    "leakage_h",
    "secondary_cap_f",
    "core_loss_ohm",
    "turns_ratio",
)

def require_candidate(raw: str) -> dict:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("candidate JSON must be an object")
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"missing candidate fields: {missing}")
    cid = str(data["candidate_id"])
    if not re.fullmatch(r"HA100X-[A-Za-z0-9._-]{6,80}", cid):
        raise ValueError(f"unsafe candidate_id: {cid!r}")
    numeric = {}
    for key in REQUIRED[1:]:
        value = float(data[key])
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{key} must be finite and > 0")
        numeric[key] = value
    if not 5.0 <= numeric["turns_ratio"] <= 20.0:
        raise ValueError("turns_ratio outside bounded research range")
    if not 1.0 <= numeric["magnetizing_h"] <= 100.0:
        raise ValueError("magnetizing_h outside bounded research range")
    if not 1e-6 <= numeric["leakage_h"] <= 0.1:
        raise ValueError("leakage_h outside bounded research range")
    if not 1e-13 <= numeric["secondary_cap_f"] <= 1e-8:
        raise ValueError("secondary_cap_f outside bounded research range")
    return {"candidate_id": cid, **numeric}

def candidate_header(c: dict) -> str:
    return f"""#pragma once

#include <JuceHeader.h>
#include <array>
#include <complex>
#include <cmath>
#include <stdexcept>

namespace vl2a
{{
class HA100XPreHostModel
{{
public:
    void prepare(double sr)
    {{
        dark.prepare(sr, kDarkLoadOhm);
        bright.prepare(sr, kBrightLoadOhm);

        const auto darkRef = std::abs(analogTransfer(1000.0, kDarkLoadOhm));
        const auto normalization = darkRef > 1.0e-12 ? 1.0 / darkRef : 1.0;
        dark.setOutputScale(normalization);
        bright.setOutputScale(normalization);
        reset();
    }}

    void reset() noexcept
    {{
        dark.reset();
        bright.reset();
    }}

    float process(float x, float t4ResistanceOhm) noexcept
    {{
        const auto yd = dark.process(x);
        const auto yb = bright.process(x);

        constexpr double rDark = 4.7e6;
        constexpr double rBright = 900.0;
        const auto r = juce::jlimit(rBright, rDark, static_cast<double>(t4ResistanceOhm));
        const auto denom = std::log(rDark) - std::log(rBright);
        const auto w = denom > 1.0e-12
            ? juce::jlimit(0.0, 1.0, (std::log(rDark) - std::log(r)) / denom)
            : 0.0;

        return static_cast<float>((1.0 - w) * yd + w * yb);
    }}

    static constexpr const char* candidateId() noexcept {{ return "{c['candidate_id']}"; }}
    static constexpr double primaryDcrOhm() noexcept {{ return {c['primary_dcr_ohm']:.17g}; }}
    static constexpr double secondaryDcrOhm() noexcept {{ return {c['secondary_dcr_ohm']:.17g}; }}
    static constexpr double magnetizingH() noexcept {{ return {c['magnetizing_h']:.17g}; }}
    static constexpr double leakageH() noexcept {{ return {c['leakage_h']:.17g}; }}
    static constexpr double secondaryCapF() noexcept {{ return {c['secondary_cap_f']:.17g}; }}
    static constexpr double coreLossOhm() noexcept {{ return {c['core_loss_ohm']:.17g}; }}
    static constexpr double turnsRatio() noexcept {{ return {c['turns_ratio']:.17g}; }}

private:
    class ThirdOrderIIR
    {{
    public:
        void prepare(double sr, double loadOhm)
        {{
            constexpr double Rp = {c['primary_dcr_ohm']:.17g};
            constexpr double Rs = {c['secondary_dcr_ohm']:.17g};
            constexpr double Lm = {c['magnetizing_h']:.17g};
            constexpr double Ll = {c['leakage_h']:.17g};
            constexpr double C  = {c['secondary_cap_f']:.17g};
            constexpr double Rc = {c['core_loss_ohm']:.17g};
            constexpr double n  = {c['turns_ratio']:.17g};
            constexpr double Rsrc = kSourceOhm;
            const double Rl = loadOhm;
            const double K = 2.0 * sr;

            const double a3 = C*Ll*Lm*Rc*Rl*n*n + C*Ll*Lm*Rl*Rs;
            const double a2 =
                C*Ll*Rc*Rl*Rs
                + C*Lm*Rc*Rl*Rp*n*n
                + C*Lm*Rc*Rl*Rs
                + C*Lm*Rc*Rl*Rsrc*n*n
                + C*Lm*Rl*Rp*Rs
                + C*Lm*Rl*Rs*Rsrc
                + Ll*Lm*Rc*n*n
                + Ll*Lm*Rl
                + Ll*Lm*Rs;
            const double a1 =
                C*Rc*Rl*Rp*Rs
                + C*Rc*Rl*Rs*Rsrc
                + Ll*Rc*Rl
                + Ll*Rc*Rs
                + Lm*Rc*Rl
                + Lm*Rc*Rp*n*n
                + Lm*Rc*Rs
                + Lm*Rc*Rsrc*n*n
                + Lm*Rl*Rp
                + Lm*Rl*Rsrc
                + Lm*Rp*Rs
                + Lm*Rs*Rsrc;
            const double a0 =
                Rc*Rl*Rp + Rc*Rl*Rsrc + Rc*Rp*Rs + Rc*Rs*Rsrc;
            const double b1 = Lm*Rc*Rl*n;

            const double k2 = K*K;
            const double k3 = k2*K;
            const double d0 = a3*k3 + a2*k2 + a1*K + a0;
            const double d1 = -3.0*a3*k3 - a2*k2 + a1*K + 3.0*a0;
            const double d2 = 3.0*a3*k3 - a2*k2 - a1*K + 3.0*a0;
            const double d3 = -a3*k3 + a2*k2 - a1*K + a0;
            const double nk = b1*K;

            if (! std::isfinite(d0) || std::abs(d0) < 1.0e-30)
                throw std::runtime_error("HA100X pre-host digital denominator is invalid");

            b = {{ nk/d0, nk/d0, -nk/d0, -nk/d0 }};
            a = {{ 1.0, d1/d0, d2/d0, d3/d0 }};
            reset();
        }}

        void setOutputScale(double s) noexcept {{ outputScale = s; }}

        void reset() noexcept
        {{
            x.fill(0.0);
            y.fill(0.0);
        }}

        float process(float input) noexcept
        {{
            const double v = input;
            double out =
                b[0]*v
                + b[1]*x[0]
                + b[2]*x[1]
                + b[3]*x[2]
                - a[1]*y[0]
                - a[2]*y[1]
                - a[3]*y[2];

            if (! std::isfinite(out))
            {{
                reset();
                return 0.0f;
            }}

            x[2] = x[1]; x[1] = x[0]; x[0] = v;
            y[2] = y[1]; y[1] = y[0]; y[0] = out;
            out *= outputScale;
            return static_cast<float>(out);
        }}

    private:
        std::array<double, 4> b {{ 0.0, 0.0, 0.0, 0.0 }};
        std::array<double, 4> a {{ 1.0, 0.0, 0.0, 0.0 }};
        std::array<double, 3> x {{ 0.0, 0.0, 0.0 }};
        std::array<double, 3> y {{ 0.0, 0.0, 0.0 }};
        double outputScale = 1.0;
    }};

    static constexpr double kSourceOhm = 150.0;
    static constexpr double kDarkLoadOhm = 48590.0;
    static constexpr double kBrightLoadOhm = 34900.0;

    static std::complex<double> parallelZ(std::complex<double> a, std::complex<double> b)
    {{
        if (std::abs(a) <= 1.0e-30 || std::abs(b) <= 1.0e-30)
            return {{0.0, 0.0}};
        return 1.0 / (1.0/a + 1.0/b);
    }}

    static std::complex<double> analogTransfer(double frequencyHz, double loadOhm)
    {{
        constexpr double pi = 3.1415926535897932384626433832795;
        constexpr double Rp = {c['primary_dcr_ohm']:.17g};
        constexpr double Rs = {c['secondary_dcr_ohm']:.17g};
        constexpr double Lm = {c['magnetizing_h']:.17g};
        constexpr double Ll = {c['leakage_h']:.17g};
        constexpr double C  = {c['secondary_cap_f']:.17g};
        constexpr double Rc = {c['core_loss_ohm']:.17g};
        constexpr double n  = {c['turns_ratio']:.17g};
        constexpr double Rsrc = kSourceOhm;

        const auto jw = std::complex<double>(0.0, 2.0*pi*frequencyHz);
        const auto zc = 1.0 / (jw*C);
        const auto zload = parallelZ({{loadOhm, 0.0}}, zc);
        const auto zsecondary = std::complex<double>(Rs, 0.0) + zload;
        const auto zref = zsecondary / (n*n);
        const auto zmag = parallelZ({{Rc, 0.0}}, jw*Lm);
        const auto zshunt = parallelZ(zmag, zref);
        const auto zseries = std::complex<double>(Rsrc + Rp, 2.0*pi*frequencyHz*Ll);
        const auto vp = zshunt / (zseries + zshunt);
        const auto vsec = n * vp;
        return vsec * zload / zsecondary;
    }}

    ThirdOrderIIR dark;
    ThirdOrderIIR bright;
}};
}}
"""

def probe_cpp() -> str:
    return r"""#include <JuceHeader.h>
#include "LA2AEngine.h"
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {
constexpr double kPi = 3.14159265358979323846;

struct HarmonicResult { double gainDb=0.0; double thdPct=0.0; bool finite=true; };
struct EngineResult { HarmonicResult harmonic; double finalGrDb=0.0; double maxGrDb=0.0; };

HarmonicResult analyse(const std::vector<float>& samples,double inputAmplitude,double frequency,double sampleRate,std::size_t start) {
    HarmonicResult result;
    const auto count=samples.size()-start;
    std::array<double,9> ss{},cc{};
    for(std::size_t i=start;i<samples.size();++i){
        const auto t=double(i-start)/sampleRate;
        const auto v=double(samples[i]);
        if(!std::isfinite(v)){ result.finite=false; return result; }
        for(int h=1;h<=8;++h){
            const auto ph=2.0*kPi*frequency*double(h)*t;
            ss[size_t(h)]+=v*std::sin(ph); cc[size_t(h)]+=v*std::cos(ph);
        }
    }
    std::array<double,9> amp{};
    for(int h=1;h<=8;++h) amp[size_t(h)]=2.0*std::hypot(ss[size_t(h)],cc[size_t(h)])/std::max<std::size_t>(count,1);
    const auto fundamental=std::max(amp[1],1e-30);
    double hp=0.0; for(int h=2;h<=8;++h) hp+=amp[size_t(h)]*amp[size_t(h)];
    result.gainDb=20.0*std::log10(fundamental/std::max(inputAmplitude,1e-30));
    result.thdPct=100.0*std::sqrt(hp)/fundamental;
    result.finite=std::isfinite(result.gainDb)&&std::isfinite(result.thdPct);
    return result;
}

HarmonicResult runTransformer(double inputDbfs,double frequency,double sampleRate){
#if PREHOST_CANDIDATE
    vl2a::HA100XPreHostModel transformer; transformer.prepare(sampleRate);
#else
    vl2a::TransformerModel transformer; transformer.prepare(sampleRate,12.0f,0.12f);
#endif
    const auto amplitude=std::pow(10.0,inputDbfs/20.0);
    const auto total=size_t(sampleRate*3.0), analysis=size_t(sampleRate);
    std::vector<float> output(total);
    for(size_t i=0;i<total;++i){
        const float x=float(amplitude*std::sin(2.0*kPi*frequency*double(i)/sampleRate));
#if PREHOST_CANDIDATE
        output[i]=transformer.process(x,4.7e6f);
#else
        output[i]=transformer.process(x);
#endif
    }
    return analyse(output,amplitude,frequency,sampleRate,total-analysis);
}

EngineResult runEngine(double inputDbfs,double frequency,double pr,bool limit,double sampleRate){
    vl2a::LA2AEngine engine; engine.prepare(sampleRate,1);
    vl2a::Parameters p; p.peakReduction=float(pr); p.gain=0.0f; p.limit=limit; engine.setParameters(p);
    const auto amplitude=std::pow(10.0,inputDbfs/20.0);
    const auto total=size_t(sampleRate*5.0), analysis=size_t(sampleRate);
    std::vector<float> output(total); double maxGr=0.0;
    for(size_t i=0;i<total;++i){
        float x=float(amplitude*std::sin(2.0*kPi*frequency*double(i)/sampleRate));
        engine.processFrame(x,nullptr); output[i]=x;
        maxGr=std::max(maxGr,double(engine.getGainReductionDb()));
    }
    EngineResult r; r.harmonic=analyse(output,amplitude,frequency,sampleRate,total-analysis);
    r.finalGrDb=engine.getGainReductionDb(); r.maxGrDb=maxGr; return r;
}
}

int main(int argc,char** argv){
    const std::string outPath=argc>=2?argv[1]:"prehost_probe.csv";
    constexpr double sr=192000.0;
    std::ofstream f(outPath,std::ios::binary); if(!f) return 2;
    f<<std::setprecision(12);
    f<<"variant,scope,input_dbfs,frequency_hz,mode,peak_reduction,gain_db,thd_pct,final_gr_db,max_gr_db,finite\n";
#if PREHOST_CANDIDATE
    const char* variant="candidate";
#else
    const char* variant="baseline";
#endif
    for(double level:{-48.0,-18.0}) for(double freq:{30.0,1000.0,20000.0}){
        auto r=runTransformer(level,freq,sr);
        f<<variant<<",transformer,"<<level<<","<<freq<<",NA,0,"<<r.gainDb<<","<<r.thdPct<<",0,0,"<<(r.finite?1:0)<<"\n";
    }
    for(double level:{-48.0,-18.0}) for(double freq:{30.0,1000.0,15000.0}){
        auto r=runEngine(level,freq,0.0,false,sr);
        f<<variant<<",engine,"<<level<<","<<freq<<",COMP,0,"<<r.harmonic.gainDb<<","<<r.harmonic.thdPct<<","<<r.finalGrDb<<","<<r.maxGrDb<<","<<(r.harmonic.finite?1:0)<<"\n";
    }
    for(bool limit:{false,true}){
        auto r=runEngine(-18.0,1000.0,50.0,limit,sr);
        f<<variant<<",engine,-18,1000,"<<(limit?"LIMIT":"COMP")<<",50,"<<r.harmonic.gainDb<<","<<r.harmonic.thdPct<<","<<r.finalGrDb<<","<<r.maxGrDb<<","<<(r.harmonic.finite?1:0)<<"\n";
    }
    return 0;
}
"""

def probe_cmake() -> str:
    text = r"""cmake_minimum_required(VERSION 3.22)
project(VL2APreHostProbe VERSION 0.1.0 LANGUAGES C CXX)
if (NOT DEFINED JUCE_PATH)
  message(FATAL_ERROR "JUCE_PATH is required")
endif()
if (NOT DEFINED BASELINE_ENGINE_DIR OR NOT DEFINED CANDIDATE_ENGINE_DIR)
  message(FATAL_ERROR "BASELINE_ENGINE_DIR and CANDIDATE_ENGINE_DIR are required")
endif()
add_subdirectory(@{JUCE_PATH} JUCE)
function(add_probe target engine_dir candidate)
  juce_add_console_app(@{target} PRODUCT_NAME "@{target}")
  juce_generate_juce_header(@{target})
  target_sources(@{target} PRIVATE prehost_probe.cpp "@{engine_dir}/LA2AEngine.cpp")
  target_include_directories(@{target} PRIVATE "@{engine_dir}")
  target_compile_features(@{target} PRIVATE cxx_std_17)
  target_compile_definitions(@{target} PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 PREHOST_CANDIDATE=@{candidate})
  target_link_libraries(@{target} PRIVATE juce::juce_dsp juce::juce_audio_basics juce::juce_core)
endfunction()
add_probe(vl2a_prehost_baseline "@{BASELINE_ENGINE_DIR}" 0)
add_probe(vl2a_prehost_candidate "@{CANDIDATE_ENGINE_DIR}" 1)
"""
    return text.replace("@", "$")

def patch_engine(root: Path, candidate: dict) -> None:
    source = root / "vl2a_lineamp_v01" / "Source"
    header = source / "LA2AEngine.h"
    cpp = source / "LA2AEngine.cpp"
    if not header.exists() or not cpp.exists():
        raise FileNotFoundError("VL2A RC2 engine files not found")

    (source / "HA100XPreHostModel.h").write_text(candidate_header(candidate), encoding="utf-8")

    h = header.read_text(encoding="utf-8")
    include_anchor = '#include "LineAmplifierDSP.h"'
    if '#include "HA100XPreHostModel.h"' not in h:
        if include_anchor not in h:
            raise RuntimeError("LineAmplifierDSP include anchor missing")
        h = h.replace(include_anchor, include_anchor + '\n#include "HA100XPreHostModel.h"', 1)
    field_anchor = "    TransformerModel inputTransformer[2];"
    if field_anchor not in h:
        raise RuntimeError("inputTransformer field anchor missing")
    h = h.replace(field_anchor, "    HA100XPreHostModel inputTransformer[2];", 1)
    header.write_text(h, encoding="utf-8")

    c = cpp.read_text(encoding="utf-8")
    prepare_anchor = "    for (auto& t : inputTransformer)       t.prepare(sr, 12.0f, 0.12f);"
    if prepare_anchor not in c:
        raise RuntimeError("input transformer prepare anchor missing")
    c = c.replace(prepare_anchor, "    for (auto& t : inputTransformer)       t.prepare(sr);", 1)

    process_anchor = "        transformed[ch] = inputTransformer[ch].process(in[ch]);"
    replacement = (
        "        transformed[ch] = inputTransformer[ch].process(\n"
        "            in[ch], t4.resistanceOhms());"
    )
    if process_anchor not in c:
        raise RuntimeError("input transformer process anchor missing")
    c = c.replace(process_anchor, replacement, 1)
    cpp.write_text(c, encoding="utf-8")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--candidate-json", required=True)
    p.add_argument("--track-id", required=True)
    p.add_argument("--source-ref", required=True)
    args = p.parse_args()

    root = Path(args.root).resolve()
    candidate = require_candidate(args.candidate_json)
    patch_engine(root, candidate)

    lab = root / "Research" / "17_PreHostHA100X"
    lab.mkdir(parents=True, exist_ok=True)
    (lab / "prehost_probe.cpp").write_text(probe_cpp(), encoding="utf-8")
    (lab / "CMakeLists.txt").write_text(probe_cmake(), encoding="utf-8")

    manifest = {
        "schema_version": "1.0",
        "classification": "EXPERIMENTAL_PREHOST_CANDIDATE_NOT_PRODUCT_ADOPTION",
        "track_id": args.track_id,
        "source_ref": args.source_ref,
        "candidate": candidate,
        "model": {
            "family": "HA100X_LINEAR_LTI_LOAD_AWARE_PREHOST",
            "source_ohm_design_choice": 150.0,
            "dark_secondary_load_ohm": 48590.0,
            "bright_secondary_load_ohm": 34900.0,
            "load_interpolation": "log_T4_resistance_crossfade_between_two_stable_LTI_filters",
            "midband_normalization": "dark_load_1k_analog_reference",
            "nonlinearity": "LOCKED_OFF",
            "hysteresis": "LOCKED_OFF",
        },
        "authority": {
            "automatic_product_decision": False,
            "automatic_release_decision": False,
            "product_branch_write": False,
            "research_staging_only": True,
        },
    }
    (lab / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
