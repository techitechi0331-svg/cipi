#pragma once

#include <JuceHeader.h>
#include <cmath>

namespace cipi::dsp
{
class CrestFactorDetector
{
public:
    void prepare (double newSampleRate)
    {
        sampleRate = newSampleRate > 0.0 ? newSampleRate : 44100.0;
        updateCoefficient();
        reset();
    }

    void reset() noexcept
    {
        rmsPower = 0.0f;
        peakPower = 0.0f;
        currentCrestSquared = 2.0f;
    }

    void setIntegrationTimeMs (float newMs) noexcept
    {
        integrationMs = juce::jlimit (1.0f, 2000.0f, newMs);
        updateCoefficient();
    }

    float process (float sample) noexcept
    {
        const auto x = std::abs (sample);
        const auto x2 = x * x;
        const auto oneMinus = 1.0f - coefficient;

        rmsPower = coefficient * rmsPower + oneMinus * x2;
        peakPower = juce::jmax (x2, coefficient * peakPower + oneMinus * x2);

        if (rmsPower <= powerFloor)
        {
            currentCrestSquared = 2.0f;
            return currentCrestSquared;
        }

        currentCrestSquared = juce::jlimit (
            1.0f,
            maxCrestSquared,
            peakPower / juce::jmax (rmsPower, powerFloor));

        return currentCrestSquared;
    }

    float getCrestSquared() const noexcept
    {
        return currentCrestSquared;
    }

    float getTransientFactor() const noexcept
    {
        const auto normalisedCrest = juce::jmax (currentCrestSquared, 2.0f) / 2.0f;
        return juce::jlimit (
            0.0f,
            1.0f,
            std::log2 (normalisedCrest) * 0.5f);
    }

private:
    void updateCoefficient() noexcept
    {
        const auto tau = static_cast<double> (integrationMs) * 0.001;
        coefficient = static_cast<float> (
            std::exp (-1.0 / juce::jmax (1.0, tau * sampleRate)));
    }

    double sampleRate { 44100.0 };
    float integrationMs { 200.0f };
    float coefficient { 0.0f };
    float rmsPower { 0.0f };
    float peakPower { 0.0f };
    float currentCrestSquared { 2.0f };

    static constexpr float powerFloor = 1.0e-12f;
    static constexpr float maxCrestSquared = 1000.0f;
};
}
