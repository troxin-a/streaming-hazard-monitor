from pathlib import Path

from shared.base.urls import BaseURL


class UserURL(BaseURL):
    """User URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_list: str = '/'
        self.user_create: str = '/'
        self.current_user: str = '/me/'
        self.user_detail: str = '/{uuid}/'
        self.user_update: str = '/{uuid}/'
        self.user_delete: str = '/{uuid}/'


user_url = UserURL(Path(__file__).parent.parent.name)
