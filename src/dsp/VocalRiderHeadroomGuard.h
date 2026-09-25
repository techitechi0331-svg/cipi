#pragma once

#include <algorithm>
#include <cmath>

namespace cipi::dsp
{
class VocalRiderHeadroomGuard
{
public:
    void prepare (double newSampleRate, int newLookaheadSamples) noexcept
    {
        sampleRate = newSampleRate > 1000.0 ? newSampleRate : 44100.0;
        lookaheadSamples = std::max (1, newLookaheadSamples);
        reset();
    }

    void reset() noexcept
    {
        limitDb = unrestrictedRideDb;
        targetDb = unrestrictedRideDb;
        holdSamples = 0;
    }

    float process (float futurePeakAbs, float outputGainLinear, float requestedRideDb) noexcept
    {
        if (! std::isfinite (futurePeakAbs))
            futurePeakAbs = 0.0f;
        if (! std::isfinite (outputGainLinear) || outputGainLinear <= 0.0f)
            outputGainLinear = 1.0f;
        if (! std::isfinite (requestedRideDb))
            requestedRideDb = 0.0f;

        const auto inputPeakDb = gainToDb (std::max (std::abs (futurePeakAbs), 1.0e-12f));
        const auto outputGainDb = gainToDb (std::max (outputGainLinear, 1.0e-12f));
        const auto safeRideDb = clamp (
            safetyCeilingDb - inputPeakDb - outputGainDb,
            minimumRideLimitDb,
            unrestrictedRideDb);

        if (safeRideDb < targetDb)
        {
            targetDb = safeRideDb;
            holdSamples = lookaheadSamples;
        }
        else if (holdSamples > 0)
        {
            --holdSamples;
        }
        else
        {
            targetDb = unrestrictedRideDb;
        }

        const auto dt = static_cast<float> (1.0 / sampleRate);
        const auto rate = targetDb < limitDb
                        ? attackRateDbPerSecond
                        : releaseRateDbPerSecond;
        const auto maxDelta = rate * dt;
        limitDb += clamp (targetDb - limitDb, -maxDelta, maxDelta);

        return std::min (requestedRideDb, limitDb);
    }

    float getCurrentLimitDb() const noexcept { return limitDb; }

private:
    static float clamp (float value, float lo, float hi) noexcept
    {
        return std::min (hi, std::max (lo, value));
    }

    static float gainToDb (float gain) noexcept
    {
        return 20.0f * static_cast<float> (std::log10 (std::max (gain, 1.0e-12f)));
    }

    static constexpr float safetyCeilingDb = -0.25f;
    static constexpr float unrestrictedRideDb = 12.0f;
    static constexpr float minimumRideLimitDb = -24.0f;
    static constexpr float attackRateDbPerSecond = 600.0f;
    static constexpr float releaseRateDbPerSecond = 12.0f;

    double sampleRate { 44100.0 };
    int lookaheadSamples { 1 };
    int holdSamples { 0 };
    float limitDb { unrestrictedRideDb };
    float targetDb { unrestrictedRideDb };
};
} // namespace cipi::dsp
