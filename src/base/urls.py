class BaseURL:
    """Base URL."""
    module = ''

    def __init__(self, *args, **kwargs):
        self.url = '/api/'

    def __call__(self, *args, **kwargs):
        if not self.module:
            self.url = '/api'
        return self.url + self.module
