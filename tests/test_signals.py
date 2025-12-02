from release_sentinel.signals import ServiceSignals, StaticSignalProvider


def test_static_signal_provider_defaults() -> None:
    provider = StaticSignalProvider()
    signals = provider.for_service("unknown")
    assert signals.service == "unknown"
    assert signals.slo_breached is False


def test_static_signal_provider_register() -> None:
    provider = StaticSignalProvider()
    provider.register(
        ServiceSignals(
            service="api",
            slo_breached=True,
            open_incidents=2,
            in_freeze=False,
        )
    )
    signals = provider.for_service("api")
    assert signals.slo_breached is True
    assert signals.open_incidents == 2




