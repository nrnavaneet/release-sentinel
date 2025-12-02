## Operations Guide

This document outlines how platform teams are expected to operate Release
Sentinel as part of their deployment workflows. Some aspects are left
intentionally under-specified to create realistic ambiguity for the Ambiguous
Coding Task project.

### Typical Workflow

1. CI builds the application artifacts and publishes a release plan YAML file.
2. The release engineer reviews and, if needed, edits risk levels in the plan.
3. A pipeline stage runs:

   ```bash
   release-sentinel evaluate configs/release_plan.yaml --policies configs/policies.yaml
   ```

4. If the command exits with a non-zero status, the deployment is blocked and
   an Azure Boards work item *should* be created referencing the failed plan.

### On-Call Expectations

- High and critical risk services should generally be shipped with `canary`
  rollout mode, though teams occasionally use blue-green for backward-
  incompatible changes. The policy files show examples for both, but the exact
  enforcement rules are still evolving.
- When a service is in SLO breach or has an active incident, only low-risk
  emergency changes should proceed. How this maps to numeric risk levels is not
  yet uniformly defined.
- Change windows currently use simple names like `weekday-business-hours`. The
  temporal semantics (time zones, holidays, etc.) are maintained in a separate
  calendar system and are not modelled in this repository.

### Known Gaps

- The Azure Boards integration is limited to returning synthetic work item IDs.
  The operations policy nonetheless expects auto-created tickets to contain
  full context and owner routing.
- Policy risk thresholds are defined per service but do not currently vary by
  environment (e.g. staging vs production); different teams interpret this
  differently.
- While both numeric and textual risk levels are allowed, there is no single
  documented mapping between them in this repo—SREs rely on tribal knowledge.




