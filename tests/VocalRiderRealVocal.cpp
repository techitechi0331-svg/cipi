#include <JuceHeader.h>
#include "../src/dsp/VocalRiderCore.h"
#include "../src/dsp/VocalRiderHeadroomGuard.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

namespace
{
constexpr int processBlockSize = 256;

struct Metrics
{
    float peakDb = -120.0f;
    float rmsDb = -120.0f;
    float crestDb = 0.0f;
    float active400StdDb = 0.0f;
    float active400P90P10Db = 0.0f;
    bool finite = true;
    std::int64_t clippedSamples = 0;
};

struct Preset
{
    const char* name;
    float amount;
};

struct RenderResult
{
    juce::AudioBuffer<float> audio;
    int latencySamples = 0;
    std::vector<float> gainTraceDb;
    bool finite = true;
};

float gainToDb (double gain)
{
    if (! std::isfinite (gain) || gain <= 1.0e-12)
        return -120.0f;
    return static_cast<float> (20.0 * std::log10 (gain));
}

float percentile (std::vector<float> values, double p)
{
    if (values.empty())
        return 0.0f;

    std::sort (values.begin(), values.end());
    const auto x = juce::jlimit (0.0, 1.0, p) * static_cast<double> (values.size() - 1);
    const auto i0 = static_cast<std::size_t> (std::floor (x));
    const auto i1 = std::min (i0 + 1, values.size() - 1);
    const auto frac = static_cast<float> (x - static_cast<double> (i0));
    return values[i0] + (values[i1] - values[i0]) * frac;
}

float standardDeviation (const std::vector<float>& values)
{
    if (values.size() < 2)
        return 0.0f;

    double mean = 0.0;
    for (const auto x : values)
        mean += x;
    mean /= static_cast<double> (values.size());

    double variance = 0.0;
    for (const auto x : values)
    {
        const auto d = static_cast<double> (x) - mean;
        variance += d * d;
    }

    variance /= static_cast<double> (values.size());
    return static_cast<float> (std::sqrt (variance));
}

Metrics analyse (const juce::AudioBuffer<float>& buffer,
                 const juce::AudioBuffer<float>& activityReference,
                 double sampleRate)
{
    Metrics m;
    const auto channels = std::min (buffer.getNumChannels(), activityReference.getNumChannels());
    const auto samples = std::min (buffer.getNumSamples(), activityReference.getNumSamples());

    if (channels <= 0 || samples <= 0)
    {
        m.finite = false;
        return m;
    }

    double sumSq = 0.0;
    std::int64_t count = 0;
    float peak = 0.0f;

    for (int ch = 0; ch < channels; ++ch)
    {
        const auto* ptr = buffer.getReadPointer (ch);
        for (int i = 0; i < samples; ++i)
        {
            const auto x = ptr[i];
            if (! std::isfinite (x))
            {
                m.finite = false;
                continue;
            }

            peak = std::max (peak, std::abs (x));
            sumSq += static_cast<double> (x) * static_cast<double> (x);
            ++count;

            if (std::abs (x) > 1.0f)
                ++m.clippedSamples;
        }
    }

    const auto rms = count > 0 ? std::sqrt (sumSq / static_cast<double> (count)) : 0.0;
    m.peakDb = gainToDb (peak);
    m.rmsDb = gainToDb (rms);
    m.crestDb = m.peakDb - m.rmsDb;

    const auto window = std::max (1, static_cast<int> (std::lround (sampleRate * 0.400)));
    std::vector<float> activeWindowDb;

    for (int pos = 0; pos < samples; pos += window)
    {
        const auto n = std::min (window, samples - pos);

        double refSq = 0.0;
        double sigSq = 0.0;
        std::int64_t refCount = 0;
        std::int64_t sigCount = 0;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto* ref = activityReference.getReadPointer (ch);
            const auto* sig = buffer.getReadPointer (ch);

            for (int i = 0; i < n; ++i)
            {
                const auto r = ref[pos + i];
                const auto s = sig[pos + i];

                if (std::isfinite (r))
                {
                    refSq += static_cast<double> (r) * r;
                    ++refCount;
                }

                if (std::isfinite (s))
                {
                    sigSq += static_cast<double> (s) * s;
                    ++sigCount;
                }
            }
        }

        if (refCount <= 0 || sigCount <= 0)
            continue;

        const auto refDb = gainToDb (std::sqrt (refSq / static_cast<double> (refCount)));
        if (refDb <= -58.0f)
            continue;

        activeWindowDb.push_back (
            gainToDb (std::sqrt (sigSq / static_cast<double> (sigCount))));
    }

    if (activeWindowDb.size() >= 4)
    {
        m.active400StdDb = standardDeviation (activeWindowDb);
        m.active400P90P10Db = percentile (activeWindowDb, 0.90)
                            - percentile (activeWindowDb, 0.10);
    }

    return m;
}

RenderResult render (const juce::AudioBuffer<float>& source,
                     double sampleRate,
                     float amount)
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (sampleRate);

    RenderResult result;
    result.latencySamples = std::max (1, static_cast<int> (std::lround (sampleRate * 0.050)));

    cipi::dsp::VocalRiderHeadroomGuard headroomGuard;
    headroomGuard.prepare (sampleRate, result.latencySamples);

    const auto channels = source.getNumChannels();
    const auto totalSamples = source.getNumSamples() + result.latencySamples;

    result.audio.setSize (channels, totalSamples);
    result.audio.clear();
    result.gainTraceDb.reserve (static_cast<std::size_t> (totalSamples));

    juce::AudioBuffer<float> delay (channels, result.latencySamples);
    delay.clear();
    int write = 0;

    for (int n = 0; n < totalSamples; ++n)
    {
        float linkedAbs = 0.0f;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = n < source.getNumSamples() ? source.getSample (ch, n) : 0.0f;
            if (std::isfinite (input))
                linkedAbs = std::max (linkedAbs, std::abs (input));
        }

        const auto requestedRideDb = rider.processSample (linkedAbs, amount);
        const auto gainDb = headroomGuard.process (linkedAbs, 1.0f, requestedRideDb);
        result.finite = result.finite && std::isfinite (gainDb);
        result.gainTraceDb.push_back (gainDb);

        const auto gain = juce::Decibels::decibelsToGain (gainDb);

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = n < source.getNumSamples() ? source.getSample (ch, n) : 0.0f;
            auto* delayPtr = delay.getWritePointer (ch);
            const auto delayed = delayPtr[write];
            delayPtr[write] = std::isfinite (input) ? input : 0.0f;

            const auto y = delayed * gain;
            if (! std::isfinite (y))
            {
                result.finite = false;
                result.audio.setSample (ch, n, 0.0f);
            }
            else
            {
                result.audio.setSample (ch, n, y);
            }
        }

        if (++write >= result.latencySamples)
            write = 0;
    }

    return result;
}

juce::AudioBuffer<float> delayedReference (const juce::AudioBuffer<float>& source,
                                           int latencySamples)
{
    juce::AudioBuffer<float> delayed (source.getNumChannels(),
                                      source.getNumSamples() + latencySamples);
    delayed.clear();

    for (int ch = 0; ch < source.getNumChannels(); ++ch)
        delayed.copyFrom (ch, latencySamples, source, ch, 0, source.getNumSamples());

    return delayed;
}

double activeRms (const juce::AudioBuffer<float>& activityReference,
                  const juce::AudioBuffer<float>& signal)
{
    const auto channels = std::min (activityReference.getNumChannels(), signal.getNumChannels());
    const auto samples = std::min (activityReference.getNumSamples(), signal.getNumSamples());

    double sumSq = 0.0;
    std::int64_t count = 0;

    for (int i = 0; i < samples; ++i)
    {
        float refPeak = 0.0f;
        for (int ch = 0; ch < channels; ++ch)
            refPeak = std::max (refPeak, std::abs (activityReference.getSample (ch, i)));

        if (gainToDb (refPeak) <= -58.0f)
            continue;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto x = signal.getSample (ch, i);
            if (! std::isfinite (x))
                continue;
            sumSq += static_cast<double> (x) * x;
            ++count;
        }
    }

    return count > 0 ? std::sqrt (sumSq / static_cast<double> (count)) : 0.0;
}

float linearPeak (const juce::AudioBuffer<float>& buffer)
{
    float peak = 0.0f;
    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
        for (int i = 0; i < buffer.getNumSamples(); ++i)
            peak = std::max (peak, std::abs (buffer.getSample (ch, i)));
    return peak;
}

float maxAbsoluteDifference (const juce::AudioBuffer<float>& a,
                             const juce::AudioBuffer<float>& b)
{
    const auto channels = std::min (a.getNumChannels(), b.getNumChannels());
    const auto samples = std::min (a.getNumSamples(), b.getNumSamples());

    float maxDiff = 0.0f;
    for (int ch = 0; ch < channels; ++ch)
        for (int i = 0; i < samples; ++i)
            maxDiff = std::max (maxDiff, std::abs (a.getSample (ch, i) - b.getSample (ch, i)));
    return maxDiff;
}

bool writeWav (const juce::File& file,
               const juce::AudioBuffer<float>& buffer,
               double sampleRate)
{
    file.deleteFile();
    auto stream = std::make_unique<juce::FileOutputStream> (file);
    if (! stream->openedOk())
        return false;

    juce::WavAudioFormat wav;
    auto options = juce::AudioFormatWriterOptions()
                       .withSampleRate (sampleRate)
                       .withNumChannels (buffer.getNumChannels())
                       .withBitsPerSample (24);

    auto writer = wav.createWriterFor (stream, options);
    if (writer == nullptr)
        return false;

    return writer->writeFromAudioSampleBuffer (buffer, 0, buffer.getNumSamples());
}

float gainMatchForListening (juce::AudioBuffer<float>& reference,
                             juce::AudioBuffer<float>& processed)
{
    const auto rmsA = activeRms (reference, reference);
    const auto rmsB = activeRms (reference, processed);

    const auto matchGain = (rmsA > 1.0e-12 && rmsB > 1.0e-12)
                         ? static_cast<float> (rmsA / rmsB)
                         : 1.0f;

    processed.applyGain (matchGain);

    const auto peak = std::max (linearPeak (reference), linearPeak (processed));
    if (peak > 0.95f)
    {
        const auto shared = 0.95f / peak;
        reference.applyGain (shared);
        processed.applyGain (shared);
    }

    return gainToDb (matchGain);
}

float maxGainSpeed (const std::vector<float>& gainTrace, double sampleRate)
{
    float maxSpeed = 0.0f;
    for (std::size_t i = 1; i < gainTrace.size(); ++i)
        maxSpeed = std::max (
            maxSpeed,
            static_cast<float> (std::abs (gainTrace[i] - gainTrace[i - 1]) * sampleRate));
    return maxSpeed;
}

std::string csvFloat (float value)
{
    std::ostringstream ss;
    ss << std::fixed << std::setprecision (4) << value;
    return ss.str();
}

juce::String safeName (juce::String name)
{
    return name.retainCharacters ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_");
}
} // namespace

int main (int argc, char** argv)
{
    if (argc < 3)
    {
        std::cerr << "Usage: CIPIVocalRiderRealVocal <output-dir> <wav> [wav ...]\n";
        return 2;
    }

    const juce::File outputDir (juce::String::fromUTF8 (argv[1]));
    if (! outputDir.createDirectory())
    {
        std::cerr << "Unable to create output directory\n";
        return 2;
    }

    const std::array<Preset, 4> presets {{
        { "Amount0", 0.00f },
        { "Amount25", 0.25f },
        { "Amount50", 0.50f },
        { "Amount75", 0.75f }
    }};

    juce::AudioFormatManager formats;
    formats.registerBasicFormats();

    std::ostringstream csv;
    csv << "file,preset,duration_s,input_peak_db,input_rms_db,input_crest_db,"
           "input_active400_std_db,input_active400_p90_p10_db,"
           "output_peak_db,output_rms_db,output_crest_db,"
           "output_active400_std_db,output_active400_p90_p10_db,"
           "ride_abs_p50_db,ride_abs_p95_db,ride_abs_max_db,max_ride_speed_db_s,"
           "clipped_samples,amount0_max_abs_diff,ab_active_rms_match_db,status\n";

    int filesProcessed = 0;
    int casesRun = 0;
    int hardFailures = 0;
    int clipWarnings = 0;

    for (int arg = 2; arg < argc; ++arg)
    {
        const juce::File inputFile (juce::String::fromUTF8 (argv[arg]));
        std::unique_ptr<juce::AudioFormatReader> reader (formats.createReaderFor (inputFile));

        if (reader == nullptr)
        {
            std::cerr << "Unable to read " << inputFile.getFullPathName() << "\n";
            ++hardFailures;
            continue;
        }

        const auto channels = juce::jlimit (1, 2, static_cast<int> (reader->numChannels));
        const auto maxSamples = static_cast<juce::int64> (std::lround (reader->sampleRate * 120.0));
        const auto length64 = std::min (reader->lengthInSamples, maxSamples);

        if (length64 <= 0 || length64 > std::numeric_limits<int>::max())
        {
            ++hardFailures;
            continue;
        }

        const auto samples = static_cast<int> (length64);
        juce::AudioBuffer<float> source (channels, samples);
        source.clear();

        if (! reader->read (&source, 0, samples, 0, true, true))
        {
            ++hardFailures;
            continue;
        }

        ++filesProcessed;
        const auto duration = static_cast<double> (samples) / reader->sampleRate;

        for (const auto& preset : presets)
        {
            ++casesRun;
            auto rendered = render (source, reader->sampleRate, preset.amount);
            auto reference = delayedReference (source, rendered.latencySamples);

            const auto inputMetrics = analyse (reference, reference, reader->sampleRate);
            const auto outputMetrics = analyse (rendered.audio, reference, reader->sampleRate);

            std::vector<float> absRide;
            absRide.reserve (rendered.gainTraceDb.size());
            for (const auto g : rendered.gainTraceDb)
                absRide.push_back (std::abs (g));

            const auto rideP50 = percentile (absRide, 0.50);
            const auto rideP95 = percentile (absRide, 0.95);
            const auto rideMax = absRide.empty() ? 0.0f : *std::max_element (absRide.begin(), absRide.end());
            const auto rideSpeed = maxGainSpeed (rendered.gainTraceDb, reader->sampleRate);

            float amount0Diff = 0.0f;
            if (preset.amount == 0.0f)
                amount0Diff = maxAbsoluteDifference (reference, rendered.audio);

            float abMatchDb = 0.0f;
            bool pass = rendered.finite && inputMetrics.finite && outputMetrics.finite;

            if (preset.amount == 0.0f && amount0Diff > 1.0e-6f)
                pass = false;

            if (outputMetrics.clippedSamples > 0)
                ++clipWarnings;

            if (std::string (preset.name) == "Amount50")
            {
                auto a = reference;
                auto b = rendered.audio;
                abMatchDb = gainMatchForListening (a, b);

                const auto base = safeName (inputFile.getFileNameWithoutExtension());
                const auto aFile = outputDir.getChildFile (base + "_A_original_delay_aligned.wav");
                const auto bFile = outputDir.getChildFile (base + "_B_VocalRider_Amount50_activeRMSmatched.wav");

                if (! writeWav (aFile, a, reader->sampleRate)
                    || ! writeWav (bFile, b, reader->sampleRate))
                    pass = false;
            }

            if (! pass)
                ++hardFailures;

            csv << inputFile.getFileName().toStdString() << ","
                << preset.name << ","
                << std::fixed << std::setprecision (3) << duration << ","
                << csvFloat (inputMetrics.peakDb) << ","
                << csvFloat (inputMetrics.rmsDb) << ","
                << csvFloat (inputMetrics.crestDb) << ","
                << csvFloat (inputMetrics.active400StdDb) << ","
                << csvFloat (inputMetrics.active400P90P10Db) << ","
                << csvFloat (outputMetrics.peakDb) << ","
                << csvFloat (outputMetrics.rmsDb) << ","
                << csvFloat (outputMetrics.crestDb) << ","
                << csvFloat (outputMetrics.active400StdDb) << ","
                << csvFloat (outputMetrics.active400P90P10Db) << ","
                << csvFloat (rideP50) << ","
                << csvFloat (rideP95) << ","
                << csvFloat (rideMax) << ","
                << csvFloat (rideSpeed) << ","
                << outputMetrics.clippedSamples << ","
                << csvFloat (amount0Diff) << ","
                << csvFloat (abMatchDb) << ","
                << (pass ? "PASS" : "FAIL") << "\n";
        }
    }

    if (! outputDir.getChildFile ("real_vocal_metrics.csv").replaceWithText (csv.str()))
        return 2;

    std::ostringstream summary;
    summary << "CIPI Vocal Rider Real Vocal Validation\n"
            << "=======================================\n"
            << "Files processed: " << filesProcessed << "\n"
            << "DSP cases: " << casesRun << "\n"
            << "Hard failures: " << hardFailures << "\n"
            << "Cases containing >0 dBFS samples: " << clipWarnings << "\n\n"
            << "Hard gates:\n"
            << "- finite input/output and finite gain trace\n"
            << "- Amount0 is delay-only with <= 1e-6 max absolute difference\n"
            << "- Amount50 delay-aligned, active-RMS matched A/B files render successfully\n\n"
            << "Clipping is recorded as a research warning rather than hidden by a limiter. "
               "If real-vocal cases clip, a peak-safe positive-ride policy must be researched before completion.\n"
            << "Objective metrics are engineering evidence, not a substitute for human listening.\n";

    if (! outputDir.getChildFile ("summary.txt").replaceWithText (summary.str()))
        return 2;

    std::cout << summary.str();
    return hardFailures == 0 ? 0 : 1;
}
