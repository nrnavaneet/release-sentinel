"""
Service readiness and external signal modelling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ServiceSignals:
    service: str
    slo_breached: bool
    open_incidents: int
    in_freeze: bool


class SignalProvider:
    """
    Abstract provider of readiness signals.

    For the sample project we include a simple in-memory provider. In real
    deployments, this would pull from SLO/error-budget backends, incident
    management tools, and deployment-freeze calendars.
    """

    def for_service(self, name: str) -> ServiceSignals:  # pragma: no cover - interface
        raise NotImplementedError


class StaticSignalProvider(SignalProvider):
    def __init__(self, mapping: Optional[Dict[str, ServiceSignals]] = None):
        self._mapping: Dict[str, ServiceSignals] = mapping or {}

    def register(self, signals: ServiceSignals) -> None:
        self._mapping[signals.service] = signals

    def for_service(self, name: str) -> ServiceSignals:
        return self._mapping.get(
            name,
            ServiceSignals(
                service=name,
                slo_breached=False,
                open_incidents=0,
                in_freeze=False,
            ),
        )




