#pragma once
#include <JuceHeader.h>
#include <cmath>

namespace cipi::dsp
{
class EnvelopeFollower
{
public:
    void prepare (double newSampleRate)
    {
        sampleRate = newSampleRate > 0.0 ? newSampleRate : 44100.0;
        reset();
        updateCoefficients();
    }

    void reset (float value = 0.0f) noexcept { state = value; }

    void setAttackRelease (float attackMs, float releaseMs) noexcept
    {
        attack = juce::jmax (0.01f, attackMs);
        release = juce::jmax (0.01f, releaseMs);
        updateCoefficients();
    }

    float process (float x) noexcept
    {
        x = std::abs (x);
        const auto coeff = x > state ? attackCoeff : releaseCoeff;
        state = coeff * state + (1.0f - coeff) * x;
        return state;
    }

private:
    void updateCoefficients() noexcept
    {
        const auto makeCoeff = [this] (float ms)
        {
            const auto tau = static_cast<double> (ms) * 0.001;
            return static_cast<float> (std::exp (-1.0 / (tau * sampleRate)));
        };
        attackCoeff = makeCoeff (attack);
        releaseCoeff = makeCoeff (release);
    }

    double sampleRate { 44100.0 };
    float attack { 5.0f }, release { 80.0f };
    float attackCoeff { 0.0f }, releaseCoeff { 0.0f };
    float state { 0.0f };
};
}
