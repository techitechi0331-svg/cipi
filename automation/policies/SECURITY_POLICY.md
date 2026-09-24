# Autonomous Research Security Policy

- Never push directly to `main`.
- Use least-privilege credentials. Workers do not need administration, secrets, workflow-write, ruleset-write, or repository-settings access.
- Do not run untrusted pull-request code in a secrets-bearing context.
- Do not weaken a validator or threshold from a worker branch.
- Never commit credentials, private keys, access tokens, or client-identifiable audio.
- Production/release decisions remain outside the worker.
