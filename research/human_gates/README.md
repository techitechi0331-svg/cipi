# CIPI Human Gate Decisions

Human Gate decisions are append-only human-review records.

## Safety boundary

A Human Gate record may document that a declared gate was completed, rejected, or deferred.
It never grants automatic product-write authority, automatic knowledge promotion, or automatic release authority.

Only `RESEARCH_JOB` gates with the latest decision `outcome: COMPLETE` are removed from the Continuity projection.
`AUTONOMOUS_TRACK` decisions are recorded for review/audit only because a stopped research track requires a separate, explicit replay/continuation contract before it can safely resume.

Every submission is bound to the exact Continuity `generation_id` and `source_state_digest` seen by the reviewer. Stale submissions fail closed.
