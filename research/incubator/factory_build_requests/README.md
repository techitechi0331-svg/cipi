# Factory Build Requests

An authorized build request is the transport object consumed by a future generic
JUCE Factory build workflow.

Each request contains:

- `plugin_contract.json`
- `factory_build_authorization.json`

A request means only **build and technical validation are authorized**. It does not
grant:

- final product approval;
- product release authority;
- Cubase confirmation;
- listening/audio-quality approval;
- CIPI knowledge promotion.

The Factory must revalidate the authorization and pinned source provenance before
building.
