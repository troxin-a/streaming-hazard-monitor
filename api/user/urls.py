from pathlib import Path

from shared.base.urls import BaseURL


class UserURL(BaseURL):
    """User URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_list: str = '/'


user_url = UserURL()
