from pathlib import Path

import pytest

from release_sentinel.config import PolicyConfig, ReleasePlan, load_policies, load_release_plan


def test_load_policies(tmp_path: Path) -> None:
  content = """
default_max_risk: low
services:
  - service: api
    max_risk: 2
"""
  file = tmp_path / "policies.yaml"
  file.write_text(content, encoding="utf-8")

  cfg = load_policies(file)
  assert isinstance(cfg, PolicyConfig)
  assert cfg.default_max_risk == "low"


def test_invalid_numeric_risk(tmp_path: Path) -> None:
  content = """
default_max_risk: 10
"""
  file = tmp_path / "policies.yaml"
  file.write_text(content, encoding="utf-8")

  with pytest.raises(ValueError):
    load_policies(file)


def test_load_release_plan(tmp_path: Path) -> None:
  content = """
id: "rel-1"
environment: staging
requested_by: "me@example.com"
at: "2025-01-01T00:00:00Z"
services: []
"""
  file = tmp_path / "plan.yaml"
  file.write_text(content, encoding="utf-8")

  plan = load_release_plan(file)
  assert isinstance(plan, ReleasePlan)
  assert plan.environment == "staging"




