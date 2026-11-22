#include <JuceHeader.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <vector>
#include <string>
#include "Vocal73DSP.h"

struct Result { double rms = 0, peak = 0; bool finite = true; int latency = 0; };
static Result measure(double sr, int bs, int channels, bool analog, int hpf, float color,
                      double freq, double seconds)
{
    Vocal73DSP dsp;
    dsp.prepare(sr, bs, channels);
    Result result;
    result.latency = dsp.getLatencySamples();
    const int total = static_cast<int>(sr * seconds);
    double sumsq = 0;
    long long count = 0;
    for (int offset = 0; offset < total; offset += bs) {
        const int n = std::min(bs, total - offset);
        juce::AudioBuffer<float> buffer(channels, n);
        for (int c = 0; c < channels; ++c)
            for (int i = 0; i < n; ++i) {
                const double t = (offset + i) / sr;
                const double signal = 0.12 * std::sin(juce::MathConstants<double>::twoPi * freq * t);
                buffer.setSample(c, i, static_cast<float>(signal));
            }
        dsp.process(buffer, 0.0f, color, 0.0f, hpf, analog);
        for (int c = 0; c < channels; ++c)
            for (int i = 0; i < n; ++i) {
                const double x = buffer.getSample(c, i);
                if (!std::isfinite(x)) result.finite = false;
                if (offset + i >= static_cast<int>(0.1 * sr)) {
                    sumsq += x * x;
                    result.peak = std::max(result.peak, std::abs(x));
                    ++count;
                }
            }
    }
    result.rms = count ? std::sqrt(sumsq / count) : 0;
    return result;
}
int main() {
    std::puts("sample_rate,block_size,channels,analog,hpf_choice,color_percent,freq_hz,rms,peak,latency_samples,finite");
    bool pass = true;
    for (double sr : {48000.0, 96000.0})
      for (int bs : {32, 256, 2048})
       for (int ch : {1, 2})
        for (int analog : {0, 1})
         for (int hpf : {0, 2})
          for (float color : {0.0f, 50.0f})
           for (double freq : {80.0, 1000.0}) {
              auto r = measure(sr, bs, ch, analog != 0, hpf, color, freq, 0.25);
              std::printf("%.0f,%d,%d,%d,%d,%.0f,%.0f,%.9g,%.9g,%d,%d\n",
                 sr, bs, ch, analog, hpf, color, freq, r.rms, r.peak, r.latency, r.finite ? 1 : 0);
              if (!r.finite || !std::isfinite(r.rms) || r.latency < 0) pass = false;
           }
    return pass ? EXIT_SUCCESS : EXIT_FAILURE;
}
