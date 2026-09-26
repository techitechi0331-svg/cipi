# Factory Build Authorizations

A Factory Build Authorization is a separate non-automation approval that permits a
validated Plugin Contract candidate to enter the JUCE Factory manufacturing and
technical-validation line.

It does **not** authorize release or establish product quality.

Requirements:

- source Contract Candidate + handoff receipt must match and revalidate;
- all handoff source hashes must still match the original proposal/decision/evidence/review;
- authority must be `HUMAN` or `ASSISTANT_REVIEW`;
- `approved_for_factory_build=true`;
- `automatic_approval=false`;
- `final_product_decision=false`;
- `product_release_authority=false`;
- `cubase_confirmed=false`;
- `listening_confirmed=false`.

The authorization record pins the SHA-256 of the Contract Candidate, handoff receipt
and authorization review. A later mutation of those source files invalidates the
authorization.
