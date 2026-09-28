# SM57 / Zenodo 4633508 authoritative-rights audit — 2026-09-29

## Decision

**BLOCKED — authoritative dataset license / product-linked model-fit permission is not yet verified.**

Do not enable `MIC-SIM-MEASURED-SM57-001` from this audit.
Do not treat the secondary CC BY 4.0 claim as sufficient authority for commercial/product-linked fitting.
Do not dispatch the real 1.5 GB archive ingest workflow while the rights state is `UNVERIFIED`.

This is a rights/provenance gate only. It does not reject the scientific value of the dataset.

## Authoritative evidence checked

### Zenodo dataset record

Primary record:
- https://zenodo.org/records/4633508
- DOI: `10.5281/zenodo.4633508`
- Dataset: *Multi-Angle, Multi-Distance Microphone Impulse Response Dataset*

Current rendered record evidence:
- the dataset is publicly downloadable;
- an attribution note asks users publishing results to cite the relevant references;
- incorporation into a new dataset is described with attribution/citation expectations;
- the archive is `Microphone_Impulse_Responses.zip`;
- published MD5 is `c66c4f46be850aa25022145431b93caa`;
- the rendered `Rights -> License` field does **not expose a license value** in the evidence snapshot available on 2026-09-29.

Therefore this audit cannot prove:
- unrestricted modification/derivative processing rights;
- commercial use rights;
- redistribution rights;
- product-linked model-fitting rights;
- derived-parameter commercialization rights.

### University of Surrey paper record

Paper record:
- https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/A-multi-angle-multi-distance-dataset-of-microphone/99648852502346
- paper DOI: `10.17743/jaes.2022.0027`

The University of Surrey record labels the **Author's Accepted Manuscript** as `CC BY V4.0`.
That is authoritative evidence for the manuscript copy exposed there, not sufficient evidence that the Zenodo dataset bytes themselves carry the same license.

Do not transfer the paper-manuscript license to the dataset by inference.

## Secondary / supporting evidence

A current Hugging Face mirror describes the `madir/` source derived from Zenodo 4633508 as `CC-BY-4.0`.

This is useful corroborating evidence but is not authoritative enough for CIPI's commercial/product-linked rights gate because:
- it is a republisher/secondary source;
- it may reflect the mirror author's interpretation or inherited metadata;
- CIPI has not verified the same license value on the primary Zenodo dataset record.

The IoSR project page confirms the project and points to the Zenodo archive, but does not close the explicit license gap.

## Scientific status remains positive

The rights block does not change the scientific-source facts already registered:
- Shure SM57 is included in the measurement set;
- quasi-anechoic IR measurements exist;
- angles span 0 to 355 degrees in 5-degree steps;
- documented distances are 0.5 m, 1.25 m and 5 m;
- rendered IRs are 48 kHz and available as raw/normalised variants;
- the source is the highest-value currently identified Tier-A SM57 controlled dataset candidate.

The dataset therefore remains:
- `SOURCE_FACT` for existence/method/SM57 inclusion;
- `CANDIDATE` for future controlled MEASURED ingestion;
- **not yet approved** for product-linked model fitting.

## Acceptable evidence that can close this gate

At least one authoritative route must explicitly establish the dataset reuse terms:

1. primary Zenodo metadata exposing a concrete license identifier / rights statement that covers the dataset files; or
2. an explicit University of Surrey / IoSR / dataset-author rights statement covering the dataset; or
3. direct written permission from the relevant rights holder for the required research/commercial use.

The evidence should resolve, at minimum:
- research use;
- modification / derivative processing;
- commercial use;
- redistribution of raw/derived assets;
- attribution obligations;
- use and commercialization of derived model parameters.

## No-Wait implementation status

While the rights gate remains blocked, the following safe preparation work has been completed in Mic Simulator main:

- merge commit `1c499b13b5e78a91dd3f1f40af4f9c5969ec3804`;
- rights-gated original-archive workflow;
- published-MD5 verification;
- exact ZIP-path SM57 discovery;
- per-member SHA-256 support;
- fail-closed extraction while rights are unverified;
- derived IR FFT / phase / group-delay analyzer with processing provenance;
- synthetic negative/positive tests;
- Surrey dataset registered as `CANDIDATE`, not MEASURED.

The workflow deliberately refuses network acquisition when `rights_status=UNVERIFIED` and never uploads the raw archive as an artifact.

## Remaining blockers before measured-track activation

- authoritative dataset rights verification;
- original archive acquisition only after rights PASS;
- actual SM57 archive paths from the original ZIP;
- original archive MD5 PASS;
- subset per-file hashes;
- a Mic Simulator acquisition manifest that passes direct validation;
- a **full measured-reference/model-fit execution adapter**; a preflight-only adapter is not sufficient;
- CIPI gate PASS.

Product integration, automatic promotion and automatic release remain OFF.
