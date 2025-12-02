"""
Typer CLI entrypoint for Release Sentinel.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .config import PolicyConfig, ReleasePlan, load_policies, load_release_plan
from .evaluator import evaluate_plan, render_result
from .signals import ServiceSignals, StaticSignalProvider

app = typer.Typer(help="Evaluate deployment release plans against policy.")
console = Console()


def _default_signals(plan: ReleasePlan) -> StaticSignalProvider:
    """
    Create a trivial signal provider that assumes healthy services.

    Real deployments would look up per-service SLO and incident data. For this
    reference repo we intentionally keep it simple but pluggable.
    """
    provider = StaticSignalProvider()
    for svc in plan.services:
        provider.register(
            ServiceSignals(
                service=svc.name,
                slo_breached=False,
                open_incidents=0,
                in_freeze=False,
            )
        )
    return provider


@app.command()
def evaluate(
    plan: Path = typer.Argument(..., exists=True, readable=True),
    policies: Path = typer.Option(
        ...,
        "--policies",
        "-p",
        exists=True,
        readable=True,
        help="YAML file containing release policies.",
    ),
) -> None:
    """Evaluate a release plan and print a decision table."""
    policy_cfg: PolicyConfig = load_policies(policies)
    release_plan: ReleasePlan = load_release_plan(plan)

    provider = _default_signals(release_plan)
    result = evaluate_plan(policy_cfg, release_plan, provider)
    console.print(render_result(result))

    if not result.overall_allowed:
        raise typer.Exit(code=2)


@app.command()
def show_policies(
    policies: Path = typer.Argument(..., exists=True, readable=True),
) -> None:
    """Print a summary of service policies."""
    policy_cfg = load_policies(policies)
    console.print(f"Default max risk: {policy_cfg.default_max_risk}")
    for svc in policy_cfg.services:
        console.print(
            f"- {svc.service}: max_risk={svc.max_risk}, "
            f"require_canary={svc.require_canary}, windows={svc.change_windows}"
        )




