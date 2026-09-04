import pytest

from app.core.rate_limit import _windows


@pytest.fixture(autouse=True)
def reset_rate_limits():
    _windows.clear()
    yield
    _windows.clear()
