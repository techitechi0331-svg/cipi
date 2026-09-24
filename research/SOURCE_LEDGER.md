# Source Ledger

| ID | Source | Type | Key use | Evidence |
|---|---|---|---|---|
| DRC-001 | Giannoulis, Massberg, Reiss, **Digital Dynamic Range Compressor Design—A Tutorial and Analysis**, JAES 60(6), 2012. https://aes2.org/publications/elibrary-page/?id=16354 | peer-reviewed / AES | compressor topology and analysis | E5 |
| DRC-002 | Giannoulis, Massberg, Reiss, **Parameter Automation in a Dynamic Range Compressor**, JAES 61(10), 2013. https://aes.org/publications/elibrary-page/?id=16965 | peer-reviewed / AES | signal-dependent parameter automation | E5 |
| DRC-003 | Floru, **Attack and Release Time Constants in RMS-Based Feedback Compressors**, JAES 47(10), 1999. https://aes.org/publications/elibrary-page/?id=12090 | peer-reviewed / AES | compressor time-constant models | E5 |
| DRC-004 | Bitzer, Schmidt, Simmer, **Parameter Estimation of Dynamic Range Compressors: Models, Procedures and Test Signals**, AES 120, 2006. https://secure.aes.org/forum/pubs/conventions/?elib=13653 | peer-reviewed / AES | artificial test signals and parameter fitting | E5 |
| DRC-005 | Moffat, Sandler, **Adaptive Ballistics Control of Dynamic Range Compression for Percussive Tracks**, AES 145, 2018. https://secure.aes.org/forum/pubs/ebriefs/?elib=19748 | AES engineering brief | adaptive timing / transient control | E4 |
| DRC-006 | Bromham, Moffat, Sheng, Fazekas, **Measuring Audibility Threshold Levels for Attack and Release in a Dynamic Range Compressor**, AES 153, 2022. https://aes.org/publications/elibrary-page/?id=21958 | AES convention paper | ABX audibility / listening-test design | E5 |
| DSP-001 | Robert Bristow-Johnson, **Audio EQ Cookbook**. https://webaudio.github.io/Audio-EQ-Cookbook/audio-eq-cookbook.html | technical reference | biquad coefficients / BLT | E4 |
| AA-001 | Bilbao, Esqueda, Parker, Välimäki, **Antiderivative Antialiasing for Memoryless Nonlinearities**, IEEE SPL 24(7), 2017. https://research.aalto.fi/en/publications/antiderivative-antialiasing-for-memoryless-nonlinearities/ | peer-reviewed | ADAA | E5 |
| AA-002 | Holters, **Antiderivative Antialiasing for Stateful Systems**, 2020. https://www.mdpi.com/2076-3417/10/1/20 | peer-reviewed | stateful ADAA | E5 |
| AA-003 | Zheleznov, Bilbao, **Interpolation Filters for Antiderivative Antialiasing**, DAFx-24. https://www.dafx.de/paper-archive/details/VEph91o4UTFBAN6Fha2z_A | peer-reviewed conference | ADAA interpolation | E5 |
| JUCE-001 | JUCE `dsp::Oversampling`. https://docs.juce.com/master/classjuce_1_1dsp_1_1Oversampling.html | official SDK | oversampling and latency | E5 |
| JUCE-002 | JUCE `SmoothedValue`. https://docs.juce.com/master/classjuce_1_1SmoothedValue.html | official SDK | glitch-safe parameter smoothing | E5 |
| JUCE-003 | JUCE `dsp::DelayLine`. https://docs.juce.com/master/classdsp_1_1DelayLine.html | official SDK | delay compensation | E5 |
| JUCE-004 | JUCE `dsp::DryWetMixer`. https://docs.juce.com/master/classjuce_1_1dsp_1_1DryWetMixer.html | official SDK | latency-compensated parallel processing | E5 |
| JUCE-005 | JUCE `dsp::LinkwitzRileyFilter`. https://docs.juce.com/master/classjuce_1_1dsp_1_1LinkwitzRileyFilter.html | official SDK | TPT LR4 crossover | E5 |
| VST-001 | Steinberg VST3, **Parameters and Automation**. https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical%2BDocumentation/Parameters%2BAutomation/Index.html | official SDK | automation semantics | E5 |
| VST-002 | Steinberg VST3, **Advanced VST3 techniques**. https://steinbergmedia.github.io/vst3_dev_portal/pages/Tutorials/Advanced%2BVST%2B3%2Btechniques.html | official SDK | sample-accurate/thread-safe state | E5 |
| MET-001 | ITU-R BS.1770-5, 2023. https://www.itu.int/rec/R-REC-BS.1770-5-202311-I | standard | loudness / true peak | E5 |
| MET-002 | EBU Tech 3341 v4.0, 2023. https://tech.ebu.ch/publications/tech3341 | technical standard | meter validation | E5 |
| EQ-001 | Hafezi, Reiss, **Autonomous Multitrack Equalization Based on Masking Reduction**, JAES 63(5), 2015. https://aes.org/publications/elibrary-page/?id=17637 | peer-reviewed / AES | masking-aware adaptive EQ research | E5 |
| VOX-001 | Wolfe et al., **Vocal tract resonances in speech, singing, and playing musical instruments**, HFSP Journal, 2009. https://pmc.ncbi.nlm.nih.gov/articles/PMC2689615/ | peer-reviewed | vocal resonance / spectral-envelope context | E5 |

A repeated quotation of one original source does not count as independent corroboration.
| VA-1176-001 | Gerat, Eichas, Zölzer, **Virtual Analog Modeling of a UREI 1176LN Dynamic Range Control System**, AES 143, 2017. https://aes.org/publications/elibrary-page/?id=19249 | peer-reviewed / AES | gray-box block-oriented 1176 modeling and validation | E5 |
| OPTO-001 | Najnudel, Müller, Hélie, Roze, **Power-Balanced Dynamic Modeling of Vactrols: Application to a VTL5C3/2**, DAFx-23. https://dafx.de/paper-archive/details/FQ0s5ZsffVCpJ_T1Far3GA | peer-reviewed conference | physical stateful optocoupler model for optical compression | E5 |
| OPTO-002 | Simionato, Fasciani, **Fully Conditioned and Low-Latency Black-Box Modeling of Analog Compression**, DAFx-23. https://www.dafx.de/paper-archive/details/1iUC09PiIdeqD8hEE-xSsg | peer-reviewed conference | parameter-conditioned real-time optical compressor modeling | E5 |

