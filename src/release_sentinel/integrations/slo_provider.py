"""
Placeholder for external SLO provider integrations.

The current implementation intentionally does not talk to real backends. Teams
are expected to replace this module with concrete integrations (e.g. to error-
budget APIs), which is a natural source of ambiguity for extension tasks.

For now, the rest of the codebase relies on `StaticSignalProvider` from
`release_sentinel.signals` for deterministic behaviour.
"""

