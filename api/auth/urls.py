from pathlib import Path

from shared.base.urls import BaseURL


class AuthURL(BaseURL):
    """Auth URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registration: str = '/registration/'
        self.login: str = '/login/'
        self.refresh: str = '/token/refresh/'


auth_url = AuthURL()
