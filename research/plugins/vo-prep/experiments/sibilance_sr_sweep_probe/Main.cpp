#include <JuceHeader.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace
{
constexpr int blockSize = 512;
constexpr double tailSeconds = 0.30;

struct Args
{
    juce::String voPrepPath;
    juce::String voPriProPath;
    juce::String outPath;
};

struct RenderResult
{
    std::vector<float> samples;
    int latencySamples = 0;
};

struct Row
{
    int sampleRate = 0;
    double sibilanceAmount = 0.0;
    double prepEventAttenuationDb = 0.0;
    double chainVsPriEventDeltaDb = 0.0;
    double chainVsPriPostDeltaDb = 0.0;
    bool finite = true;
};

double dbToGain (double db)
{
    return std::pow (10.0, db / 20.0);
}

double rmsDb (const std::vector<float>& values,
              double sampleRate,
              double startSeconds,
              double endSeconds,
              int latencySamples = 0)
{
    const auto begin = std::clamp (
        static_cast<long long> (std::floor (startSeconds * sampleRate)) + latencySamples,
        0LL,
        static_cast<long long> (values.size()));

    const auto end = std::clamp (
        static_cast<long long> (std::floor (endSeconds * sampleRate)) + latencySamples,
        begin,
        static_cast<long long> (values.size()));

    if (end <= begin)
        return -120.0;

    long double power = 0.0;
    for (auto i = begin; i < end; ++i)
    {
        const auto x = static_cast<long double> (values[static_cast<size_t> (i)]);
        power += x * x;
    }

    power /= static_cast<long double> (end - begin);
    return 10.0 * std::log10 (std::max (static_cast<double> (power), 1.0e-12));
}

double eventEnvelope (double t, double start, double end, double attack, double release)
{
    if (t < start || t >= end)
        return 0.0;

    if (t < start + attack)
        return (t - start) / attack;

    if (t > end - release)
        return (end - t) / release;

    return 1.0;
}

std::vector<float> makeSibilanceCase (int sr)
{
    const auto contentSamples = static_cast<size_t> (std::llround (2.10 * sr));
    const auto totalSamples = static_cast<size_t> (
        std::llround ((2.10 + tailSeconds) * sr));

    std::vector<float> y (totalSamples, 0.0f);
    constexpr double frequencies[] { 5200.0, 6100.0, 7200.0, 8400.0, 9700.0, 11200.0 };

    for (size_t i = 0; i < contentSamples; ++i)
    {
        const auto t = static_cast<double> (i) / sr;
        double vowel = 0.0;

        for (int harmonic = 1; harmonic < 35; ++harmonic)
        {
            const auto frequency = 180.0 * harmonic;
            if (frequency >= 12000.0)
                break;

            vowel += (0.12 / harmonic)
                   * std::sin (2.0 * juce::MathConstants<double>::pi * frequency * t);
        }

        double sibilant = 0.0;
        for (size_t f = 0; f < std::size (frequencies); ++f)
            sibilant += 0.08 * std::sin (
                2.0 * juce::MathConstants<double>::pi * frequencies[f] * t
                + static_cast<double> (f) * 0.7);

        const auto env = eventEnvelope (t, 0.8, 0.95, 0.005, 0.015);
        y[i] = static_cast<float> (vowel * (1.0 - 0.9 * env) + sibilant * env);
    }

    return y;
}

Args parseArgs (int argc, char** argv)
{
    Args args;

    for (int i = 1; i + 1 < argc; i += 2)
    {
        const juce::String key (argv[i]);
        const juce::String value (argv[i + 1]);

        if (key == "--voprep")
            args.voPrepPath = value;
        else if (key == "--vopripro")
            args.voPriProPath = value;
        else if (key == "--out")
            args.outPath = value;
        else
            throw std::runtime_error ("unknown argument: " + key.toStdString());
    }

    if (args.voPrepPath.isEmpty() || args.voPriProPath.isEmpty() || args.outPath.isEmpty())
        throw std::runtime_error ("required: --voprep <bundle> --vopripro <bundle> --out <json>");

    return args;
}

class PluginLoader
{
public:
    PluginLoader()
    {
        juce::addHeadlessDefaultFormatsToManager (formats);
    }

    juce::PluginDescription describe (const juce::String& path)
    {
        for (auto* format : formats.getFormats())
        {
            if (! format->getName().equalsIgnoreCase ("VST3"))
                continue;

            juce::OwnedArray<juce::PluginDescription> found;
            format->findAllTypesForFile (found, path);

            if (found.size() != 1)
                throw std::runtime_error (
                    "expected exactly one VST3 type at "
                    + path.toStdString()
                    + ", found "
                    + std::to_string (found.size()));

            return *found[0];
        }

        throw std::runtime_error ("JUCE VST3 host format unavailable");
    }

    std::unique_ptr<juce::AudioPluginInstance> create (const juce::PluginDescription& description,
                                                        double sampleRate)
    {
        juce::String error;
        auto instance = formats.createPluginInstance (
            description, sampleRate, blockSize, error);

        if (instance == nullptr)
            throw std::runtime_error (
                "failed to instantiate "
                + description.name.toStdString()
                + ": "
                + error.toStdString());

        return instance;
    }

private:
    juce::AudioPluginFormatManager formats;
};

void setExactParameter (juce::AudioPluginInstance& plugin,
                        const juce::String& expectedName,
                        float normalizedValue)
{
    juce::AudioProcessorParameter* match = nullptr;
    int matches = 0;

    for (auto* parameter : plugin.getParameters())
    {
        if (parameter->getName (128) == expectedName)
        {
            match = parameter;
            ++matches;
        }
    }

    if (matches != 1 || match == nullptr)
        throw std::runtime_error (
            "parameter contract mismatch in "
            + plugin.getName().toStdString()
            + ": expected exactly one '"
            + expectedName.toStdString()
            + "', found "
            + std::to_string (matches));

    match->setValueNotifyingHost (juce::jlimit (0.0f, 1.0f, normalizedValue));
}

void configureVoPrep (juce::AudioPluginInstance& plugin, float sibilanceAmount)
{
    setExactParameter (plugin, "Input", 0.5f);
    setExactParameter (plugin, "Plosive", 0.0f);
    setExactParameter (plugin, "Level", 0.0f);
    setExactParameter (plugin, "Sibilance", sibilanceAmount);
    setExactParameter (plugin, "Subsonic", 0.0f);
    setExactParameter (plugin, "Output", 0.5f);
}

void configureVoPriPro (juce::AudioPluginInstance& plugin)
{
    setExactParameter (plugin, "Amount", 0.5f);
    setExactParameter (plugin, "Character", 0.5f);
    setExactParameter (plugin, "Input", 0.5f);
    setExactParameter (plugin, "Output", 0.5f);
}

void prepareStereo (juce::AudioPluginInstance& plugin, double sr)
{
    juce::AudioProcessor::BusesLayout layout;
    layout.inputBuses.add (juce::AudioChannelSet::stereo());
    layout.outputBuses.add (juce::AudioChannelSet::stereo());

    if (! plugin.setBusesLayout (layout))
        throw std::runtime_error (
            "failed to set stereo bus layout for "
            + plugin.getName().toStdString());

    plugin.setNonRealtime (true);
    plugin.setRateAndBufferSizeDetails (sr, blockSize);
    plugin.prepareToPlay (sr, blockSize);
    plugin.reset();
}

RenderResult render (PluginLoader& loader,
                     const juce::PluginDescription& prepDescription,
                     const juce::PluginDescription& priDescription,
                     const std::vector<float>& input,
                     int sampleRate,
                     float sibilanceAmount,
                     bool usePrep,
                     bool usePri)
{
    std::unique_ptr<juce::AudioPluginInstance> prep;
    std::unique_ptr<juce::AudioPluginInstance> pri;
    int latency = 0;

    if (usePrep)
    {
        prep = loader.create (prepDescription, sampleRate);
        configureVoPrep (*prep, sibilanceAmount);
        prepareStereo (*prep, sampleRate);
        latency += prep->getLatencySamples();
    }

    if (usePri)
    {
        pri = loader.create (priDescription, sampleRate);
        configureVoPriPro (*pri);
        prepareStereo (*pri, sampleRate);
        latency += pri->getLatencySamples();
    }

    std::vector<float> output (input.size(), 0.0f);
    juce::MidiBuffer midi;

    for (size_t offset = 0; offset < input.size(); offset += blockSize)
    {
        const auto count = static_cast<int> (
            std::min<size_t> (blockSize, input.size() - offset));

        juce::AudioBuffer<float> buffer (2, blockSize);
        buffer.clear();

        for (int i = 0; i < count; ++i)
        {
            const auto x = input[offset + static_cast<size_t> (i)];
            buffer.setSample (0, i, x);
            buffer.setSample (1, i, x);
        }

        midi.clear();

        if (prep != nullptr)
            prep->processBlock (buffer, midi);

        if (pri != nullptr)
            pri->processBlock (buffer, midi);

        for (int i = 0; i < count; ++i)
            output[offset + static_cast<size_t> (i)] = buffer.getSample (0, i);
    }

    if (prep != nullptr)
        prep->releaseResources();

    if (pri != nullptr)
        pri->releaseResources();

    return { std::move (output), latency };
}

bool allFinite (const std::vector<float>& values)
{
    return std::all_of (values.begin(), values.end(),
                        [] (float x) { return std::isfinite (x); });
}

juce::var rowToVar (const Row& row)
{
    auto* object = new juce::DynamicObject();
    object->setProperty ("sample_rate_hz", row.sampleRate);
    object->setProperty ("sibilance_amount", row.sibilanceAmount);
    object->setProperty ("all_finite", row.finite);
    object->setProperty ("voprep_event_attenuation_db", row.prepEventAttenuationDb);
    object->setProperty ("chain_vs_vopripro_event_rms_delta_db", row.chainVsPriEventDeltaDb);
    object->setProperty ("chain_vs_vopripro_post_event_rms_delta_db", row.chainVsPriPostDeltaDb);
    return juce::var (object);
}
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juceInitialiser;

    try
    {
        const auto args = parseArgs (argc, argv);
        PluginLoader loader;

        const auto prepDescription = loader.describe (args.voPrepPath);
        const auto priDescription = loader.describe (args.voPriProPath);

        constexpr int sampleRates[] { 44100, 48000, 88200, 96000 };
        constexpr float amounts[] { 0.00f, 0.25f, 0.30f, 0.35f, 0.40f, 0.45f, 0.50f };

        std::vector<Row> rows;

        for (const auto sr : sampleRates)
        {
            const auto input = makeSibilanceCase (sr);
            const auto pri = render (
                loader, prepDescription, priDescription, input, sr, 0.0f, false, true);

            for (const auto amount : amounts)
            {
                const auto prep = render (
                    loader, prepDescription, priDescription, input, sr, amount, true, false);
                const auto chain = render (
                    loader, prepDescription, priDescription, input, sr, amount, true, true);

                Row row;
                row.sampleRate = sr;
                row.sibilanceAmount = amount;
                row.prepEventAttenuationDb =
                    rmsDb (input, sr, 0.80, 1.15, 0)
                    - rmsDb (prep.samples, sr, 0.80, 1.15, prep.latencySamples);

                row.chainVsPriEventDeltaDb =
                    rmsDb (chain.samples, sr, 0.80, 1.15, chain.latencySamples)
                    - rmsDb (pri.samples, sr, 0.80, 1.15, pri.latencySamples);

                row.chainVsPriPostDeltaDb =
                    rmsDb (chain.samples, sr, 1.35, 1.75, chain.latencySamples)
                    - rmsDb (pri.samples, sr, 1.35, 1.75, pri.latencySamples);

                row.finite = allFinite (prep.samples)
                          && allFinite (pri.samples)
                          && allFinite (chain.samples);

                rows.push_back (row);
            }
        }

        const Row* reference = nullptr;
        for (const auto& row : rows)
        {
            if (row.sampleRate == 48000 && std::abs (row.sibilanceAmount - 0.50) < 1.0e-6)
            {
                reference = &row;
                break;
            }
        }

        if (reference == nullptr)
            throw std::runtime_error ("48 kHz / 50% reference row missing");

        auto qualifies = [&] (const Row& row)
        {
            return row.finite
                && row.prepEventAttenuationDb >= 0.10
                && std::abs (row.chainVsPriEventDeltaDb) <= 0.15
                && std::abs (row.chainVsPriPostDeltaDb) <= 0.15
                && std::abs (row.prepEventAttenuationDb - reference->prepEventAttenuationDb) <= 0.05;
        };

        bool depthScalingSufficient = true;
        for (const auto sr : { 88200, 96000 })
        {
            const auto found = std::any_of (
                rows.begin(), rows.end(), [&] (const Row& row)
                {
                    return row.sampleRate == sr && qualifies (row);
                });

            depthScalingSufficient = depthScalingSufficient && found;
        }

        const auto allRowsFinite = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) { return row.finite; });

        auto* root = new juce::DynamicObject();
        root->setProperty ("schema", "voprep-sibilance-sr-sweep-v1");
        root->setProperty (
            "decision",
            allRowsFinite
                ? (depthScalingSufficient
                    ? "DEPTH_SCALING_SUFFICIENT"
                    : "DETECTOR_OR_TOPOLOGY_REVIEW")
                : "DETECTOR_OR_TOPOLOGY_REVIEW");
        root->setProperty ("voprep_plugin_name", prepDescription.name);
        root->setProperty ("vopripro_plugin_name", priDescription.name);
        root->setProperty ("reference_48k_50_event_attenuation_db", reference->prepEventAttenuationDb);
        root->setProperty ("raw_audio_persisted", false);
        root->setProperty ("product_dsp_mutated", false);

        juce::Array<juce::var> rowVars;
        for (const auto& row : rows)
            rowVars.add (rowToVar (row));
        root->setProperty ("rows", juce::var (rowVars));

        const auto json = juce::JSON::toString (juce::var (root), true);
        const juce::File outputFile (args.outPath);
        outputFile.getParentDirectory().createDirectory();

        if (! outputFile.replaceWithText (json + "\n"))
            throw std::runtime_error ("failed to write result JSON");

        std::cout << json << std::endl;
        return allRowsFinite ? 0 : 1;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Vo.Prep Sibilance SR sweep failed: " << e.what() << std::endl;
        return 1;
    }
}
