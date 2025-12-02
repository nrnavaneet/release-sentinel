## Release Sentinel Architecture

Release Sentinel models a deployment gatekeeper that sits in front of production
rollouts. It makes decisions based on:

1. **Release Plan** (`release_sentinel.config.ReleasePlan`)
   - Describes who requested the release, which environment it targets, when it
     should run, and which services are included with their risk levels and
     rollout modes (direct, canary, blue-green).

2. **Policy Configuration** (`release_sentinel.config.PolicyConfig`)
   - Defines acceptable maximum risk levels per service and environment-agnostic
     change windows.
   - Allows mixing numeric (1-5) and textual risk thresholds, which various
     teams interpret differently.

3. **Signal Providers** (`release_sentinel.signals.SignalProvider`)
   - Encapsulate SLO, incident, and deployment-freeze signals for each service.
   - The sample app ships with `StaticSignalProvider` for deterministic tests
     and local runs.

4. **Evaluator** (`release_sentinel.evaluator`)
   - Normalises risk representations and decides if each service in a plan is
     allowed or blocked.
   - Produces a `EvaluationResult` that the CLI renders via Rich.

### Extension Points

- Swap `StaticSignalProvider` for a real SLO backend or incident management
  integration.
- Implement time-aware change-window enforcement in `_window_allows` using the
  rollout timestamp from the plan.
- Use `integrations.azure_boards.AzureBoardsClient` to open tickets whenever a
  service is blocked.




