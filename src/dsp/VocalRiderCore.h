#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <limits>

namespace cipi::dsp
{
class VocalRiderCore
{
public:
    void prepare (double newSampleRate)
    {
        sampleRate = newSampleRate > 1000.0 ? newSampleRate : 44100.0;
        targetUpdateSamples = std::max (1, static_cast<int> (std::lround (sampleRate * 0.050)));
        activityHangSamples = std::max (1, static_cast<int> (std::lround (sampleRate * 0.180)));

        bodyCoeff = timeCoeff (0.120);
        phraseCoeff = timeCoeff (0.450);
        peakAttackCoeff = timeCoeff (0.001);
        peakReleaseCoeff = timeCoeff (0.050);

        targetSmoothingCoeff = std::exp (-0.050 / 2.5);

        reset();
    }

    void reset() noexcept
    {
        bodyEnergy = 0.0;
        phraseEnergy = 0.0;
        peakEnvelope = 0.0;
        targetDb = 0.0f;
        targetReady = false;
        targetCounter = 0;
        historyWrite = 0;
        historyCount = 0;
        active = false;
        activityHang = 0;
        desiredGainDb = 0.0f;
        currentGainDb = 0.0f;
        velocityDbPerSecond = 0.0f;
        currentBodyDb = -120.0f;
        currentPhraseDb = -120.0f;
        currentCrestDb = 0.0f;
    }

    float processSample (float linkedAbsSample, float amount01) noexcept
    {
        if (! std::isfinite (linkedAbsSample))
            linkedAbsSample = 0.0f;

        const auto x = std::abs (linkedAbsSample);
        const auto energy = static_cast<double> (x) * static_cast<double> (x);

        bodyEnergy = bodyCoeff * bodyEnergy + (1.0 - bodyCoeff) * energy;
        phraseEnergy = phraseCoeff * phraseEnergy + (1.0 - phraseCoeff) * energy;

        const auto peakCoeff = static_cast<double> (x) > peakEnvelope ? peakAttackCoeff : peakReleaseCoeff;
        peakEnvelope = peakCoeff * peakEnvelope + (1.0 - peakCoeff) * static_cast<double> (x);

        currentBodyDb = energyToDb (bodyEnergy);
        currentPhraseDb = energyToDb (phraseEnergy);

        const auto bodyRms = std::sqrt (std::max (bodyEnergy, minEnergy));
        currentCrestDb = static_cast<float> (
            20.0 * std::log10 ((peakEnvelope + 1.0e-12) / (bodyRms + 1.0e-12)));

        updateActivity();

        const auto shortTransient = currentBodyDb > -60.0f && currentCrestDb > 10.0f;

        if (++targetCounter >= targetUpdateSamples)
        {
            targetCounter = 0;

            if (active && ! shortTransient && std::isfinite (currentPhraseDb))
                pushTargetSample (currentPhraseDb);
        }

        amount01 = clamp (amount01, 0.0f, 1.0f);
        const auto depth = amountDepth (amount01);

        float newDesired = 0.0f;

        if (active && targetReady && depth > 0.0f)
        {
            const auto errorDb = targetDb - currentPhraseDb;
            const auto deadZoneError = applyDeadZone (errorDb, 0.65f);
            const auto rangeDb = 4.0f * depth;

            newDesired = clamp (0.85f * depth * deadZoneError, -rangeDb, rangeDb);
        }

        if (! shortTransient)
            desiredGainDb = newDesired;

        if (! active)
            desiredGainDb = 0.0f;

        updateGainTrajectory (depth);

        if (! std::isfinite (currentGainDb) || ! std::isfinite (velocityDbPerSecond))
        {
            currentGainDb = 0.0f;
            velocityDbPerSecond = 0.0f;
        }

        return currentGainDb;
    }

    float getCurrentGainDb() const noexcept { return currentGainDb; }
    float getDesiredGainDb() const noexcept { return desiredGainDb; }
    float getTargetDb() const noexcept { return targetDb; }
    float getBodyDb() const noexcept { return currentBodyDb; }
    float getPhraseDb() const noexcept { return currentPhraseDb; }
    float getCrestDb() const noexcept { return currentCrestDb; }
    bool isActive() const noexcept { return active; }
    bool isTargetReady() const noexcept { return targetReady; }

private:
    static constexpr std::size_t historyCapacity = 400;
    static constexpr double minEnergy = 1.0e-15;

    double timeCoeff (double tauSeconds) const noexcept
    {
        return std::exp (-1.0 / (std::max (tauSeconds, 1.0e-6) * sampleRate));
    }

    static float energyToDb (double energy) noexcept
    {
        return static_cast<float> (10.0 * std::log10 (std::max (energy, minEnergy)));
    }

    static float clamp (float value, float lo, float hi) noexcept
    {
        return std::min (hi, std::max (lo, value));
    }

    static float applyDeadZone (float errorDb, float deadZoneDb) noexcept
    {
        const auto magnitude = std::abs (errorDb) - deadZoneDb;
        if (magnitude <= 0.0f)
            return 0.0f;
        return std::copysign (magnitude, errorDb);
    }

    static float amountDepth (float amount01) noexcept
    {
        if (amount01 <= 0.5f)
            return amount01 * 2.0f;

        const auto upper = (amount01 - 0.5f) * 2.0f;
        return 1.0f + 0.25f * upper;
    }

    void updateActivity() noexcept
    {
        if (! active)
        {
            if (currentBodyDb > -58.0f)
            {
                active = true;
                activityHang = activityHangSamples;
            }
            return;
        }

        if (currentBodyDb > -62.0f)
        {
            activityHang = activityHangSamples;
            return;
        }

        if (activityHang > 0)
            --activityHang;

        if (activityHang <= 0)
            active = false;
    }

    void pushTargetSample (float valueDb) noexcept
    {
        history[historyWrite] = valueDb;
        historyWrite = (historyWrite + 1) % historyCapacity;
        historyCount = std::min<std::size_t> (historyCount + 1, historyCapacity);

        if (historyCount < 6)
            return;

        for (std::size_t i = 0; i < historyCount; ++i)
            scratch[i] = history[i];

        const auto middle = scratch.begin() + static_cast<std::ptrdiff_t> (historyCount / 2);
        std::nth_element (scratch.begin(), middle, scratch.begin() + static_cast<std::ptrdiff_t> (historyCount));
        const auto medianDb = *middle;

        if (! targetReady)
        {
            targetDb = medianDb;
            targetReady = true;
        }
        else
        {
            targetDb = static_cast<float> (
                targetSmoothingCoeff * targetDb + (1.0 - targetSmoothingCoeff) * medianDb);
        }
    }

    void updateGainTrajectory (float depth) noexcept
    {
        const auto dt = static_cast<float> (1.0 / sampleRate);
        const auto diff = desiredGainDb - currentGainDb;

        const auto extra = std::max (0.0f, depth - 1.0f);
        const auto maxBoostSpeed = 12.0f + 12.0f * extra;
        const auto maxCutSpeed = 16.0f + 12.0f * extra;
        constexpr float acceleration = 60.0f;
        constexpr float inactiveReturnSpeed = 5.0f;

        const auto responseSeconds = diff < 0.0f ? 0.18f : 0.24f;
        auto desiredVelocity = diff / responseSeconds;
        desiredVelocity = clamp (desiredVelocity, -maxCutSpeed, maxBoostSpeed);

        if (! active)
            desiredVelocity = clamp (desiredVelocity, -inactiveReturnSpeed, inactiveReturnSpeed);

        const auto maxDv = acceleration * dt;
        const auto dv = clamp (desiredVelocity - velocityDbPerSecond, -maxDv, maxDv);
        velocityDbPerSecond += dv;

        const auto step = velocityDbPerSecond * dt;

        if (std::abs (step) >= std::abs (diff)
            && ((step >= 0.0f && diff >= 0.0f) || (step <= 0.0f && diff <= 0.0f)))
        {
            currentGainDb = desiredGainDb;
            velocityDbPerSecond = 0.0f;
        }
        else
        {
            currentGainDb += step;
        }

        const auto hardLimit = 5.0f * std::max (depth, 0.0f);
        if (depth <= 0.0f)
        {
            currentGainDb = 0.0f;
            velocityDbPerSecond = 0.0f;
        }
        else
        {
            currentGainDb = clamp (currentGainDb, -hardLimit, hardLimit);
        }
    }

    double sampleRate { 44100.0 };
    int targetUpdateSamples { 2205 };
    int targetCounter { 0 };
    int activityHangSamples { 7938 };
    int activityHang { 0 };

    double bodyCoeff { 0.0 };
    double phraseCoeff { 0.0 };
    double peakAttackCoeff { 0.0 };
    double peakReleaseCoeff { 0.0 };
    double targetSmoothingCoeff { 0.98 };

    double bodyEnergy { 0.0 };
    double phraseEnergy { 0.0 };
    double peakEnvelope { 0.0 };

    std::array<float, historyCapacity> history {};
    std::array<float, historyCapacity> scratch {};
    std::size_t historyWrite { 0 };
    std::size_t historyCount { 0 };

    bool active { false };
    bool targetReady { false };

    float targetDb { 0.0f };
    float desiredGainDb { 0.0f };
    float currentGainDb { 0.0f };
    float velocityDbPerSecond { 0.0f };

    float currentBodyDb { -120.0f };
    float currentPhraseDb { -120.0f };
    float currentCrestDb { 0.0f };
};
} // namespace cipi::dsp
