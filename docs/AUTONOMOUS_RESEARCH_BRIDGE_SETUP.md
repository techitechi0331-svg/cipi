# Autonomous Research Bridge — one-time token setup

Autonomous Research Bridge v1 is already integrated. The remaining external dependency is a repository secret named `CIPI_CROSS_REPO_TOKEN` in `techitechi0331-svg/cipi`.

## Recommended credential

Use a fine-grained GitHub personal access token restricted to:

- Repository access: `techitechi0331-svg/melon`
- Actions: Read and write
- Contents: Read

GitHub may include Metadata: Read automatically. Do not commit the token to either repository and do not store it as a plain repository variable.

## Secret name

`CIPI_CROSS_REPO_TOKEN`

The CIPI Global DAG reads only this secret name. When absent, queued MELON work remains intact and the dashboard reports:

`EXTERNAL_BLOCK / CIPI_CROSS_REPO_TOKEN_MISSING`

When the secret becomes available, the existing queued action becomes a normal `CROSS_REPO` READY node on the next Global DAG run. No new research card or manual requeue is required.

## Current pilot safety boundary

The pilot remains bounded by the registered Research Track. Product repositories are not modified, MELON has no final-decision authority, CIPI knowledge is not promoted automatically, and Human Gates remain required for listening/host validation/product adoption.
