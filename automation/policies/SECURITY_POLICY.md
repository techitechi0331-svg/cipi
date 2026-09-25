# Autonomous Research Security Policy

- Never push directly to `main`.
- Use least-privilege credentials. Workers do not need administration, secrets, workflow-write, ruleset-write, or repository-settings access.
- Do not run untrusted pull-request code in a secrets-bearing context.
- Do not weaken a validator or threshold from a worker branch.
- Never commit credentials, private keys, access tokens, or client-identifiable audio.
- Production/release decisions remain outside the worker.

## Architect and Incubator isolation

- Research Architect may create only append-only research artifacts on `architect-bot/*` branches.
- Unknown research themes must not become executable code automatically; they stop at `NEEDS_ADAPTER`.
- Pilot and prototype execution is restricted to hard-coded allowlists.
- Plugin Incubator may not mutate existing product repositories, create official repositories, publish releases, or close Cubase/listening gates.
- Automated Incubator decisions are advisory and never final.
