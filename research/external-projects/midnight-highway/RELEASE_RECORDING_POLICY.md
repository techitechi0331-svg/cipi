# MIDNIGHT HIGHWAY — release-to-CIPI recording contract
Status: User-requested workflow policy recorded 2026-11-02, not a deployed autonomous agent.

After every future repair or version update performed in an active development task, the completion criteria are:
1. Keep the previous working game build and increment the version.
2. Reproduce defects, write specific fixes, and execute applicable tests. Separate verified results from unverified claims. Include fail cases.
3. Generate deliverable HTML + Windows package as requested. Verify archive and SHA-256 consistency, but never misrepresent a PE format check as Windows runtime test.
4. Add an append-only `RELEASE_<date>_v<version>.md` record under `research/external-projects/midnight-highway/`, with build artifacts' names and SHA-256, root causes, controls affected, test environment/results, regressions, unresolved defects and next actions.
5. Keep external game code and binaries outside public CIPI; link only to a durable, appropriately private source-of-truth repository when established.
6. Draft PR / review before merging changes into CIPI main or dispatching CIPI jobs. Do not change CIPI cross-repo registry or workflows by implication.
7. Respond to the user with the delivered build AND its CIPI record/PR link; if the CIPI write fails, disclose failure rather than claim success.

This file is an **instruction for future active collaboration**, not a background task that runs on its own. No ongoing monitoring or auto-update is asserted. Human release acceptance is a separate gate.
