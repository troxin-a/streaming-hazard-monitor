from pathlib import Path

from shared.base.urls import BaseURL


class AlertURL(BaseURL):
    """Alert URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alerts_list: str = '/'


alert_url = AlertURL(Path(__file__).parent.parent.name)
