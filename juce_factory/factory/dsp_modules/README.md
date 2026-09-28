# JUCE Factory DSP Modules

The DSP Module Registry is the allowlist between a Plugin Contract and Factory code
generation.

A module is build-eligible only when the registry entry is valid and declares:

- `certification_status=FACTORY_CERTIFIED`;
- `factory_build_eligible=true`;
- an explicitly supported Plugin Contract version;
- exact required parameter IDs;
- supported channel layouts;
- a known validation profile;
- `product_release_authority=false`.

Registration alone is not enough to generate code. The Factory generator must also
contain the exact `implementation_id` and validation-profile implementation. This
second gate prevents a newly registered or malformed module from becoming executable
manufacturing code automatically.

The canonical registry and every module spec are SHA-256 hashed into the Factory
manifest. Registry status is manufacturing metadata only and never grants release,
Cubase, listening, or CIPI knowledge-promotion authority.
