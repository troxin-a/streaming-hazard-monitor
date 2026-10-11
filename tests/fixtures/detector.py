from unittest.mock import AsyncMock

import pytest

from detector.sessions import DetectorSession


@pytest.fixture(scope='function')
def detector_session() -> AsyncMock:
    """Session of the threshold detector replaced with a mock that records level changes."""
    return AsyncMock(spec=DetectorSession)
