from types import SimpleNamespace

from plugins.memory.hindsight import HindsightMemoryProvider


def test_hindsight_limits_recall_results_when_configured():
    provider = HindsightMemoryProvider()
    provider._recall_result_limit = 5
    results = [SimpleNamespace(text=f"memory {i}") for i in range(8)]

    limited = provider._limit_recall_results(results)

    assert len(limited) == 5
    assert [r.text for r in limited] == [f"memory {i}" for i in range(5)]


def test_hindsight_does_not_limit_results_by_default():
    provider = HindsightMemoryProvider()
    provider._recall_result_limit = 0
    results = [SimpleNamespace(text=f"memory {i}") for i in range(8)]

    limited = provider._limit_recall_results(results)

    assert limited == results
