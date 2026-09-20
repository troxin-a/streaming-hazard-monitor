from pathlib import Path

from shared.base.urls import BaseURL


class TelemetryURL(BaseURL):
    """Telemetry URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telemetry: str = '/telemetry/'


telemetry_url = TelemetryURL(Path(__file__).parent.parent.name)
