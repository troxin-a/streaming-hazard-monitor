class BaseURL:
    """Base URL."""
    module = ''

    def __init__(self, root_url: str, *args, **kwargs):
        self.url = f'/{root_url}/'

    def __call__(self, *args, **kwargs):
        if not self.module:
            self.url = f'/{self.url}'
        return self.url + self.module
