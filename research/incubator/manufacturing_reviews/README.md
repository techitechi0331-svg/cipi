# Incubator Manufacturing Reviews

A Manufacturing Review is the non-automation gate between an evidence-backed
Incubator candidate and a JUCE Factory Plugin Contract **candidate**.

A valid review must:

- reference a matching non-final `INCUBATE` decision;
- reference the exact product-discrimination evidence used by that decision;
- use review authority `HUMAN` or `ASSISTANT_REVIEW`, never `AUTOMATION`;
- contain a Plugin Contract that passes the current JUCE Factory validator;
- keep automatic approval, final product decision, Factory build authority,
  release authority, Cubase confirmation and listening confirmation all false.

A Manufacturing Review does not authorize a VST3 build or release. It only allows
a versioned Contract candidate and provenance receipt to be produced.
