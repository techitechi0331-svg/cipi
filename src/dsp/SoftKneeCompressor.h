#pragma once
#include <JuceHeader.h>
#include <cmath>

namespace cipi::dsp
{
inline float gainComputerDb (float inputDb, float thresholdDb, float ratio, float kneeDb) noexcept
{
    ratio = juce::jmax (1.0f, ratio);
    kneeDb = juce::jmax (0.0f, kneeDb);

    if (kneeDb <= 0.0001f)
    {
        if (inputDb <= thresholdDb) return 0.0f;
        return (thresholdDb + (inputDb - thresholdDb) / ratio) - inputDb;
    }

    const auto halfKnee = 0.5f * kneeDb;
    const auto delta = inputDb - thresholdDb;
    if (delta <= -halfKnee) return 0.0f;
    if (delta >= halfKnee) return (thresholdDb + delta / ratio) - inputDb;

    const auto z = delta + halfKnee;
    return (1.0f / ratio - 1.0f) * z * z / (2.0f * kneeDb);
}

class GainReductionBallistics
{
public:
    void prepare (double newSampleRate)
    {
        sampleRate = newSampleRate > 0.0 ? newSampleRate : 44100.0;
        reset();
    }

    void reset() noexcept { grDb = 0.0f; }

    float process (float targetGrDb, float attackMs, float releaseMs) noexcept
    {
        targetGrDb = juce::jmax (0.0f, targetGrDb);
        const auto timeMs = targetGrDb > grDb ? attackMs : releaseMs;
        const auto tau = juce::jmax (0.01f, timeMs) * 0.001;
        const auto coeff = static_cast<float> (std::exp (-1.0 / (tau * sampleRate)));
        grDb = coeff * grDb + (1.0f - coeff) * targetGrDb;
        return grDb;
    }

    float getCurrentDb() const noexcept { return grDb; }

private:
    double sampleRate { 44100.0 };
    float grDb { 0.0f };
};
}
