"""
Core evaluation logic for release plans.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from rich.console import Console
from rich.table import Table

from .config import PolicyConfig, ReleasePlan, RiskLevel, RolloutMode, ServiceRelease
from .signals import ServiceSignals, SignalProvider


@dataclass
class ServiceDecision:
    service: str
    allowed: bool
    reason: str


@dataclass
class EvaluationResult:
    plan_id: str
    environment: str
    overall_allowed: bool
    decisions: List[ServiceDecision]


def _normalize_risk(risk: int | RiskLevel) -> int:
    if isinstance(risk, int):
        return risk
    mapping = {
        RiskLevel.LOW: 1,
        RiskLevel.MEDIUM: 2,
        RiskLevel.HIGH: 3,
        RiskLevel.CRITICAL: 4,
    }
    return mapping[risk]


def _effective_max_risk(policy_cfg: PolicyConfig, service: ServiceRelease) -> int:
    policy = policy_cfg.policy_for(service.name)
    max_risk = policy.max_risk if policy else policy_cfg.default_max_risk
    return _normalize_risk(max_risk)


def _window_allows(policy_cfg: PolicyConfig, environment: str, service: ServiceRelease) -> bool:
    policy = policy_cfg.policy_for(service.name)
    if not policy or not policy.change_windows:
        # Intentionally assumes "allowed" if no explicit windows configured.
        return True
    for window_name in policy.change_windows:
        window = policy_cfg.window_by_name(window_name)
        if window and (not window.environments or environment in window.environments):
            # Detailed time-range comparison is intentionally left out to keep
            # the project focused; this is a hook for ambiguity.
            return True
    return False


def _evaluate_service(
    policy_cfg: PolicyConfig,
    plan: ReleasePlan,
    svc: ServiceRelease,
    signals: ServiceSignals,
) -> ServiceDecision:
    risk = _normalize_risk(svc.risk)
    max_risk = _effective_max_risk(policy_cfg, svc)

    if risk > max_risk:
        return ServiceDecision(
            service=svc.name,
            allowed=False,
            reason=f"risk {risk} exceeds max {max_risk}",
        )

    if signals.slo_breached:
        return ServiceDecision(
            service=svc.name,
            allowed=False,
            reason="SLO is currently breached",
        )

    if signals.in_freeze:
        return ServiceDecision(
            service=svc.name,
            allowed=False,
            reason="deployment freeze active",
        )

    if not _window_allows(policy_cfg, plan.environment, svc):
        return ServiceDecision(
            service=svc.name,
            allowed=False,
            reason="no matching change window allows this release",
        )

    policy = policy_cfg.policy_for(svc.name)
    if policy and policy.require_canary and svc.mode == RolloutMode.DIRECT:
        return ServiceDecision(
            service=svc.name,
            allowed=False,
            reason="canary required by policy but plan uses direct rollout",
        )

    return ServiceDecision(service=svc.name, allowed=True, reason="ok")


def evaluate_plan(
    policy_cfg: PolicyConfig,
    plan: ReleasePlan,
    signal_provider: SignalProvider,
) -> EvaluationResult:
    decisions: List[ServiceDecision] = []
    for svc in plan.services:
        svc_signals = signal_provider.for_service(svc.name)
        decisions.append(_evaluate_service(policy_cfg, plan, svc, svc_signals))
    overall_allowed = all(d.allowed for d in decisions)
    return EvaluationResult(
        plan_id=plan.id,
        environment=plan.environment,
        overall_allowed=overall_allowed,
        decisions=decisions,
    )


def render_result(result: EvaluationResult) -> str:
    console = Console(record=True, width=100)
    table = Table(title=f"Release Plan {result.plan_id} ({result.environment})")
    table.add_column("Service")
    table.add_column("Allowed")
    table.add_column("Reason")
    for d in result.decisions:
        table.add_row(d.service, "yes" if d.allowed else "no", d.reason)
    console.print(table)
    return console.export_text()




