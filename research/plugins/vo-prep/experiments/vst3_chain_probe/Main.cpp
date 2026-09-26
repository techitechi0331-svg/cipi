#include <JuceHeader.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
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
    juce::String pluginName;
};

struct Row
{
    int sampleRate = 0;
    double neutralPrepDeltaDb = 0.0;
    double neutralChainVsPriDeltaDb = 0.0;
    double plosivePrepAttenDb = 0.0;
    double plosiveChainAttenDb = 0.0;
    double plosivePostDeltaDb = 0.0;
    double sibilancePrepAttenDb = 0.0;
    double sibilanceChainDeltaDb = 0.0;
    double sibilancePostDeltaDb = 0.0;
    double phrasePrepSpreadMovementDb = 0.0;
    double phraseChainSpreadMovementDb = 0.0;
    int voPrepLatencySamples = 0;
    int voPriProLatencySamples = 0;
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

double phraseSpread (const std::vector<float>& values, double sr, int latency)
{
    const std::pair<double, double> segments[] {
        { 0.65, 1.40 },
        { 1.80, 2.55 },
        { 2.95, 3.75 }
    };

    std::vector<double> levels;
    for (const auto& segment : segments)
        levels.push_back (rmsDb (values, sr, segment.first, segment.second, latency));

    const auto [lo, hi] = std::minmax_element (levels.begin(), levels.end());
    return *hi - *lo;
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

std::vector<float> makeCase (const std::string& name, int sr)
{
    const auto contentSamples = static_cast<size_t> (std::llround (4.0 * sr));
    const auto totalSamples = static_cast<size_t> (
        std::llround ((4.0 + tailSeconds) * sr));

    std::vector<float> y (totalSamples, 0.0f);
    const auto bodyAmp = dbToGain (-18.0);

    for (size_t i = static_cast<size_t> (0.40 * sr); i < contentSamples; ++i)
    {
        const auto t = static_cast<double> (i) / sr;
        y[i] = static_cast<float> (bodyAmp * std::sin (2.0 * juce::MathConstants<double>::pi * 220.0 * t));
    }

    if (name == "neutral_body")
        return y;

    if (name == "plosive_on_body")
    {
        std::fill (y.begin(), y.end(), 0.0f);

        for (size_t i = 0; i < contentSamples; ++i)
        {
            const auto t = static_cast<double> (i) / sr;
            double x = 0.04 * std::sin (2.0 * juce::MathConstants<double>::pi * 140.0 * t);

            if (t >= 0.8 && t < 0.86)
            {
                const auto u = (t - 0.8) / 0.06;
                const auto env = std::pow (std::sin (juce::MathConstants<double>::pi * u), 2.0);
                x += env * (
                    0.90 * std::sin (2.0 * juce::MathConstants<double>::pi * 45.0 * t)
                    + 0.08 * std::sin (2.0 * juce::MathConstants<double>::pi * 120.0 * t));
            }

            y[i] = static_cast<float> (x);
        }

        return y;
    }

    if (name == "sibilance_on_body")
    {
        std::fill (y.begin(), y.end(), 0.0f);
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

    if (name == "phrase_step")
    {
        for (size_t i = static_cast<size_t> (0.40 * sr); i < contentSamples; ++i)
        {
            const auto t = static_cast<double> (i) / sr;
            const auto level = t < 1.55 ? -22.0 : (t < 2.70 ? -14.0 : -20.0);
            y[i] = static_cast<float> (
                dbToGain (level)
                * std::sin (2.0 * juce::MathConstants<double>::pi * 220.0 * t));
        }

        return y;
    }

    throw std::runtime_error ("unknown test case: " + name);
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

void configureVoPrep (juce::AudioPluginInstance& plugin)
{
    setExactParameter (plugin, "Input", 0.5f);
    setExactParameter (plugin, "Plosive", 0.5f);
    setExactParameter (plugin, "Level", 0.0f);
    setExactParameter (plugin, "Sibilance", 0.5f);
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
                     bool usePrep,
                     bool usePri)
{
    std::unique_ptr<juce::AudioPluginInstance> prep;
    std::unique_ptr<juce::AudioPluginInstance> pri;
    int latency = 0;
    juce::String pluginName;

    if (usePrep)
    {
        prep = loader.create (prepDescription, sampleRate);
        configureVoPrep (*prep);
        prepareStereo (*prep, sampleRate);
        latency += prep->getLatencySamples();
        pluginName << prep->getName();
    }

    if (usePri)
    {
        pri = loader.create (priDescription, sampleRate);
        configureVoPriPro (*pri);
        prepareStereo (*pri, sampleRate);
        latency += pri->getLatencySamples();

        if (pluginName.isNotEmpty())
            pluginName << " -> ";

        pluginName << pri->getName();
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

    return { std::move (output), latency, pluginName };
}

bool allFinite (const std::vector<float>& values)
{
    return std::all_of (values.begin(), values.end(),
                        [] (float x) { return std::isfinite (x); });
}

Row runRate (PluginLoader& loader,
             const juce::PluginDescription& prepDescription,
             const juce::PluginDescription& priDescription,
             int sr)
{
    Row row;
    row.sampleRate = sr;

    const auto neutral = makeCase ("neutral_body", sr);
    const auto plosive = makeCase ("plosive_on_body", sr);
    const auto sibilance = makeCase ("sibilance_on_body", sr);
    const auto phrase = makeCase ("phrase_step", sr);

    const auto neutralPrep = render (loader, prepDescription, priDescription, neutral, sr, true, false);
    const auto neutralPri = render (loader, prepDescription, priDescription, neutral, sr, false, true);
    const auto neutralChain = render (loader, prepDescription, priDescription, neutral, sr, true, true);

    const auto plosivePrep = render (loader, prepDescription, priDescription, plosive, sr, true, false);
    const auto plosivePri = render (loader, prepDescription, priDescription, plosive, sr, false, true);
    const auto plosiveChain = render (loader, prepDescription, priDescription, plosive, sr, true, true);

    const auto sibilancePrep = render (loader, prepDescription, priDescription, sibilance, sr, true, false);
    const auto sibilancePri = render (loader, prepDescription, priDescription, sibilance, sr, false, true);
    const auto sibilanceChain = render (loader, prepDescription, priDescription, sibilance, sr, true, true);

    const auto phrasePrep = render (loader, prepDescription, priDescription, phrase, sr, true, false);
    const auto phrasePri = render (loader, prepDescription, priDescription, phrase, sr, false, true);
    const auto phraseChain = render (loader, prepDescription, priDescription, phrase, sr, true, true);

    row.voPrepLatencySamples = neutralPrep.latencySamples;
    row.voPriProLatencySamples = neutralPri.latencySamples;

    row.neutralPrepDeltaDb =
        rmsDb (neutralPrep.samples, sr, 1.0, 2.0, neutralPrep.latencySamples)
        - rmsDb (neutral, sr, 1.0, 2.0, 0);

    row.neutralChainVsPriDeltaDb =
        rmsDb (neutralChain.samples, sr, 1.0, 2.0, neutralChain.latencySamples)
        - rmsDb (neutralPri.samples, sr, 1.0, 2.0, neutralPri.latencySamples);

    row.plosivePrepAttenDb =
        rmsDb (plosive, sr, 0.80, 1.05, 0)
        - rmsDb (plosivePrep.samples, sr, 0.80, 1.05, plosivePrep.latencySamples);

    row.plosiveChainAttenDb =
        rmsDb (plosivePri.samples, sr, 0.80, 1.05, plosivePri.latencySamples)
        - rmsDb (plosiveChain.samples, sr, 0.80, 1.05, plosiveChain.latencySamples);

    row.plosivePostDeltaDb =
        rmsDb (plosiveChain.samples, sr, 1.25, 1.65, plosiveChain.latencySamples)
        - rmsDb (plosivePri.samples, sr, 1.25, 1.65, plosivePri.latencySamples);

    row.sibilancePrepAttenDb =
        rmsDb (sibilance, sr, 0.80, 1.15, 0)
        - rmsDb (sibilancePrep.samples, sr, 0.80, 1.15, sibilancePrep.latencySamples);

    row.sibilanceChainDeltaDb =
        rmsDb (sibilanceChain.samples, sr, 0.80, 1.15, sibilanceChain.latencySamples)
        - rmsDb (sibilancePri.samples, sr, 0.80, 1.15, sibilancePri.latencySamples);

    row.sibilancePostDeltaDb =
        rmsDb (sibilanceChain.samples, sr, 1.35, 1.75, sibilanceChain.latencySamples)
        - rmsDb (sibilancePri.samples, sr, 1.35, 1.75, sibilancePri.latencySamples);

    row.phrasePrepSpreadMovementDb =
        phraseSpread (phrasePrep.samples, sr, phrasePrep.latencySamples)
        - phraseSpread (phrase, sr, 0);

    row.phraseChainSpreadMovementDb =
        phraseSpread (phraseChain.samples, sr, phraseChain.latencySamples)
        - phraseSpread (phrasePri.samples, sr, phrasePri.latencySamples);

    row.finite = allFinite (neutralPrep.samples)
              && allFinite (neutralPri.samples)
              && allFinite (neutralChain.samples)
              && allFinite (plosivePrep.samples)
              && allFinite (plosivePri.samples)
              && allFinite (plosiveChain.samples)
              && allFinite (sibilancePrep.samples)
              && allFinite (sibilancePri.samples)
              && allFinite (sibilanceChain.samples)
              && allFinite (phrasePrep.samples)
              && allFinite (phrasePri.samples)
              && allFinite (phraseChain.samples);

    return row;
}

double spread (const std::vector<Row>& rows, const std::function<double (const Row&)>& getter)
{
    std::vector<double> values;
    values.reserve (rows.size());

    for (const auto& row : rows)
        values.push_back (getter (row));

    const auto [lo, hi] = std::minmax_element (values.begin(), values.end());
    return *hi - *lo;
}

juce::var rowToVar (const Row& row)
{
    auto* object = new juce::DynamicObject();
    object->setProperty ("sample_rate_hz", row.sampleRate);
    object->setProperty ("voprep_latency_samples", row.voPrepLatencySamples);
    object->setProperty ("vopripro_latency_samples", row.voPriProLatencySamples);
    object->setProperty ("all_finite", row.finite);
    object->setProperty ("neutral_voprep_only_rms_delta_db", row.neutralPrepDeltaDb);
    object->setProperty ("neutral_chain_vs_vopripro_rms_delta_db", row.neutralChainVsPriDeltaDb);
    object->setProperty ("plosive_voprep_event_attenuation_db", row.plosivePrepAttenDb);
    object->setProperty ("plosive_chain_vs_vopripro_event_attenuation_db", row.plosiveChainAttenDb);
    object->setProperty ("plosive_post_event_chain_vs_vopripro_rms_delta_db", row.plosivePostDeltaDb);
    object->setProperty ("sibilance_voprep_event_attenuation_db", row.sibilancePrepAttenDb);
    object->setProperty ("sibilance_chain_vs_vopripro_event_rms_delta_db", row.sibilanceChainDeltaDb);
    object->setProperty ("sibilance_post_event_chain_vs_vopripro_rms_delta_db", row.sibilancePostDeltaDb);
    object->setProperty ("phrase_voprep_spread_movement_db", row.phrasePrepSpreadMovementDb);
    object->setProperty ("phrase_chain_vs_vopripro_spread_movement_db", row.phraseChainSpreadMovementDb);
    return juce::var (object);
}

void writeFailure (const juce::String& path, const juce::String& message)
{
    auto* root = new juce::DynamicObject();
    root->setProperty ("schema", "voprep-actual-vst3-chain-v1");
    root->setProperty ("decision", "REJECT_OR_REVISE");
    root->setProperty ("error", message);
    root->setProperty ("raw_audio_persisted", false);
    juce::File (path).replaceWithText (juce::JSON::toString (juce::var (root), true));
}
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juceInitialiser;

    juce::String outPath;

    try
    {
        const auto args = parseArgs (argc, argv);
        outPath = args.outPath;

        PluginLoader loader;
        const auto prepDescription = loader.describe (args.voPrepPath);
        const auto priDescription = loader.describe (args.voPriProPath);

        const int sampleRates[] { 44100, 48000, 88200, 96000 };
        std::vector<Row> rows;

        for (const auto sr : sampleRates)
            rows.push_back (runRate (loader, prepDescription, priDescription, sr));

        std::map<std::string, bool> gates;
        gates["all_finite"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) { return row.finite; });

        gates["voprep_latency_zero"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return row.voPrepLatencySamples == 0;
            });

        gates["vopripro_latency_matches_1ms"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                const auto expected = static_cast<int> (
                    std::llround (row.sampleRate * 0.001));
                return std::abs (row.voPriProLatencySamples - expected) <= 1;
            });

        gates["neutral_voprep_abs_delta_le_0_10db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.neutralPrepDeltaDb) <= 0.10;
            });

        gates["neutral_chain_abs_delta_le_0_10db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.neutralChainVsPriDeltaDb) <= 0.10;
            });

        gates["plosive_voprep_event_attenuation_ge_0_25db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return row.plosivePrepAttenDb >= 0.25;
            });

        gates["plosive_chain_event_attenuation_ge_0_15db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return row.plosiveChainAttenDb >= 0.15;
            });

        gates["plosive_post_event_abs_delta_le_0_15db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.plosivePostDeltaDb) <= 0.15;
            });

        gates["sibilance_voprep_event_attenuation_ge_0_10db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return row.sibilancePrepAttenDb >= 0.10;
            });

        gates["sibilance_chain_abs_delta_le_0_15db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.sibilanceChainDeltaDb) <= 0.15;
            });

        gates["sibilance_post_event_abs_delta_le_0_15db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.sibilancePostDeltaDb) <= 0.15;
            });

        gates["phrase_voprep_abs_spread_movement_le_0_10db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.phrasePrepSpreadMovementDb) <= 0.10;
            });

        gates["phrase_chain_abs_spread_movement_le_0_10db"] = std::all_of (
            rows.begin(), rows.end(), [] (const Row& row) {
                return std::abs (row.phraseChainSpreadMovementDb) <= 0.10;
            });

        const std::function<double (const Row&)> metrics[] {
            [] (const Row& r) { return r.neutralPrepDeltaDb; },
            [] (const Row& r) { return r.neutralChainVsPriDeltaDb; },
            [] (const Row& r) { return r.plosivePrepAttenDb; },
            [] (const Row& r) { return r.plosiveChainAttenDb; },
            [] (const Row& r) { return r.plosivePostDeltaDb; },
            [] (const Row& r) { return r.sibilancePrepAttenDb; },
            [] (const Row& r) { return r.sibilanceChainDeltaDb; },
            [] (const Row& r) { return r.sibilancePostDeltaDb; },
            [] (const Row& r) { return r.phrasePrepSpreadMovementDb; },
            [] (const Row& r) { return r.phraseChainSpreadMovementDb; },
        };

        double maximumMetricSpread = 0.0;
        for (const auto& metric : metrics)
            maximumMetricSpread = std::max (maximumMetricSpread, spread (rows, metric));

        gates["cross_sample_rate_metric_spread_le_0_15db"] = maximumMetricSpread <= 0.15;

        const auto accepted = std::all_of (
            gates.begin(), gates.end(), [] (const auto& item) { return item.second; });

        auto* root = new juce::DynamicObject();
        root->setProperty ("schema", "voprep-actual-vst3-chain-v1");
        root->setProperty (
            "decision",
            accepted ? "GO_TO_REAL_VOCAL_AB" : "REJECT_OR_REVISE");
        root->setProperty ("voprep_plugin_name", prepDescription.name);
        root->setProperty ("vopripro_plugin_name", priDescription.name);
        root->setProperty ("block_size", blockSize);
        root->setProperty ("raw_audio_persisted", false);
        root->setProperty ("product_dsp_mutated", false);
        root->setProperty (
            "maximum_cross_sample_rate_metric_spread_db",
            maximumMetricSpread);

        juce::Array<juce::var> rowVars;
        for (const auto& row : rows)
            rowVars.add (rowToVar (row));
        root->setProperty ("rows", rowVars);

        auto* gateObject = new juce::DynamicObject();
        for (const auto& [name, value] : gates)
            gateObject->setProperty (juce::Identifier (name), value);
        root->setProperty ("gates", juce::var (gateObject));

        const auto json = juce::JSON::toString (juce::var (root), true);
        const juce::File outputFile (args.outPath);
        outputFile.getParentDirectory().createDirectory();

        if (! outputFile.replaceWithText (json + "\n"))
            throw std::runtime_error ("failed to write result JSON");

        std::cout << json << std::endl;
        return accepted ? 0 : 2;
    }
    catch (const std::exception& e)
    {
        const juce::String message (e.what());
        std::cerr << "Vo.Prep actual VST3 chain probe failed: "
                  << message << std::endl;

        if (outPath.isNotEmpty())
            writeFailure (outPath, message);

        return 1;
    }
}
