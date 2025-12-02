"""
Configuration models and loaders for release plans and policies.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeWindow(BaseModel):
    name: str
    start: str = Field(
        ...,
        description="Start of the window in ISO-8601 or HH:MM format (timezone handling is left to the caller).",
    )
    end: str = Field(
        ...,
        description="End of the window in ISO-8601 or HH:MM format.",
    )
    environments: List[str] = Field(default_factory=list)


class ServicePolicy(BaseModel):
    service: str
    max_risk: Union[int, RiskLevel] = Field(
        ...,
        description="Maximum tolerated risk; may be numeric (1-5) or textual.",
    )
    require_canary: bool = False
    change_windows: List[str] = Field(
        default_factory=list,
        description="Names of change windows that must allow this release.",
    )

    @field_validator("max_risk")
    @classmethod
    def validate_max_risk(cls, value: Union[int, str]) -> Union[int, RiskLevel]:
        if isinstance(value, int):
            if value < 1 or value > 5:
                raise ValueError("numeric max_risk must be between 1 and 5")
            return value
        try:
            return RiskLevel(value.lower())
        except ValueError as exc:
            raise ValueError(f"invalid risk level {value!r}") from exc


class PolicyConfig(BaseModel):
    default_max_risk: Union[int, RiskLevel] = Field(
        "medium",
        description="Fallback risk threshold if a service-specific policy is not defined.",
    )
    windows: List[ChangeWindow] = Field(default_factory=list)
    services: List[ServicePolicy] = Field(default_factory=list)

    @field_validator("default_max_risk")
    @classmethod
    def validate_default_max_risk(cls, value: Union[int, str]) -> Union[int, RiskLevel]:
        if isinstance(value, int):
            if value < 1 or value > 5:
                raise ValueError("numeric default_max_risk must be between 1 and 5")
            return value
        try:
            return RiskLevel(value.lower())
        except ValueError as exc:
            raise ValueError(f"invalid default risk level {value!r}") from exc

    def window_by_name(self, name: str) -> Optional[ChangeWindow]:
        return next((w for w in self.windows if w.name == name), None)

    def policy_for(self, service: str) -> Optional[ServicePolicy]:
        return next((p for p in self.services if p.service == service), None)


class RolloutMode(str, Enum):
    DIRECT = "direct"
    CANARY = "canary"
    BLUE_GREEN = "blue-green"


class ServiceRelease(BaseModel):
    name: str
    risk: Union[int, RiskLevel]
    mode: RolloutMode = RolloutMode.DIRECT
    metadata: Dict[str, Union[str, int, float]] = Field(default_factory=dict)

    @field_validator("risk")
    @classmethod
    def validate_risk(cls, value: Union[int, str]) -> Union[int, RiskLevel]:
        if isinstance(value, int):
            if value < 1 or value > 5:
                raise ValueError("numeric risk must be between 1 and 5")
            return value
        try:
            return RiskLevel(value.lower())
        except ValueError as exc:
            raise ValueError(f"invalid risk level {value!r}") from exc


class ReleasePlan(BaseModel):
    id: str
    environment: str
    description: Optional[str] = None
    requested_by: str
    at: str = Field(
        ...,
        description="Requested execution time (ISO-8601 or RFC3339).",
    )
    services: List[ServiceRelease] = Field(default_factory=list)


def _load_yaml(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping at root of {path}")
    return data


def load_policies(path: Union[str, Path]) -> PolicyConfig:
    p = Path(path)
    raw = _load_yaml(p)
    try:
        return PolicyConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"policy configuration invalid: {exc}") from exc


def load_release_plan(path: Union[str, Path]) -> ReleasePlan:
    p = Path(path)
    raw = _load_yaml(p)
    try:
        return ReleasePlan.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"release plan invalid: {exc}") from exc


