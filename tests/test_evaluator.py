from release_sentinel.config import PolicyConfig, ReleasePlan, ServicePolicy, ServiceRelease
from release_sentinel.evaluator import EvaluationResult, evaluate_plan
from release_sentinel.signals import ServiceSignals, StaticSignalProvider


def test_evaluator_blocks_excessive_risk() -> None:
    policy = PolicyConfig(
        default_max_risk="medium",
        services=[ServicePolicy(service="api", max_risk=2)],
    )
    plan = ReleasePlan(
        id="rel-1",
        environment="production",
        requested_by="me@example.com",
        at="2025-01-01T00:00:00Z",
        services=[
            ServiceRelease(name="api", risk=4, mode="direct"),
        ],
    )
    provider = StaticSignalProvider(
        {
            "api": ServiceSignals(
                service="api",
                slo_breached=False,
                open_incidents=0,
                in_freeze=False,
            )
        }
    )

    result: EvaluationResult = evaluate_plan(policy, plan, provider)
    assert result.overall_allowed is False
    assert result.decisions[0].allowed is False




