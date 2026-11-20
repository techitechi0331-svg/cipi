// Research-only JUCE fixture for Vocal73DSP v0.2. NOT a hardware 1073 test.
// Build instructions: see 1073-r4-juce-headless-fixture-2026-11-21.md
// No product writes; no assertions about fidelity. Uses product DSP source unchanged.
#include <JuceHeader.h>
#include "Vocal73DSP.h"
#include <cmath>
#include <iostream>
#include <iomanip>
#include <vector>
#include <algorithm>

namespace {
constexpr double fs = 48000.0;
constexpr int maxBlock = 2048;
constexpr int nSamples = 16384;
constexpr int toggleSample = 8192;

struct Render {
    std::vector<float> samples;
    int latency = -1;
};

Render render(int blockSize, bool toggleHpf, bool toggleAnalog, bool toggleColor, bool initialAnalog = true)
{
    Vocal73DSP dsp;
    dsp.prepare(fs, maxBlock, 1);
    Render result;
    result.latency = dsp.getLatencySamples();
    result.samples.reserve(nSamples);

    // Steady input for settling, with deterministic, exact block-aligned switches.
    // 8192 is divisible by all test block sizes (32, 256, 2048).
    for (int offset = 0; offset < nSamples; offset += blockSize) {
        const int count = std::min(blockSize, nSamples - offset);
        juce::AudioBuffer<float> audio(1, count);
        for (int i = 0; i < count; ++i) {
            const int t = offset + i;
            const double tone = 0.1 * std::sin(2.0 * juce::MathConstants<double>::pi * 997.0 * t / fs);
            audio.setSample(0, i, static_cast<float>(tone + 0.04));
        }
        const bool after = offset >= toggleSample;
        const int hpf = toggleHpf && after ? 2 : 0;
        const bool analog = toggleAnalog ? after : initialAnalog;
        const float color = toggleColor && after ? 100.0f : 45.0f;
        dsp.process(audio, 0.0f, color, 0.0f, hpf, analog);
        for (int i = 0; i < count; ++i)
            result.samples.push_back(audio.getSample(0, i));
    }
    return result;
}

void report(const char* name, int block, const Render& changed, const Render& baseline)
{
    double maxAbsDelta = 0.0, rms = 0.0, switchPeak = 0.0;
    bool finite = true;
    for (int i = 0; i < nSamples; ++i) {
        const double x = changed.samples[static_cast<size_t>(i)];
        const double y = baseline.samples[static_cast<size_t>(i)];
        finite = finite && std::isfinite(x);
        if (i >= toggleSample) {
            const double d = x - y;
            maxAbsDelta = std::max(maxAbsDelta, std::abs(d));
            rms += d * d;
        }
    }
    rms = std::sqrt(rms / (nSamples - toggleSample));
    // switch_window_peak is absolute signal peak, NOT click amplitude or a hardware-fidelity metric.
    for (int i = toggleSample - 8; i < toggleSample + 64; ++i)
        switchPeak = std::max(switchPeak, std::abs(static_cast<double>(changed.samples[static_cast<size_t>(i)])));
    std::cout << name << ',' << block << ',' << changed.latency << ','
              << (finite ? "true" : "false") << ',' << std::setprecision(12)
              << maxAbsDelta << ',' << rms << ',' << switchPeak << '\n';
}
} // namespace

int main()
{
    std::cout << "case,block_size,latency_samples,finite,max_abs_difference,rms_difference,switch_window_peak\n";
    for (int block : {32, 256, 2048}) {
        const auto baseline = render(block, false, false, false);
        const auto analogOffBaseline = render(block, false, false, false, false);
        report("HPF_0_TO_80", block, render(block, true, false, false), baseline);
        report("ANALOG_OFF_TO_ON", block, render(block, false, true, false, false), analogOffBaseline);
        report("COLOR_45_TO_100", block, render(block, false, false, true), baseline);
    }
    return 0;
}
