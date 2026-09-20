from shared.base.schemes import BaseScheme


class LoginResponseScheme(BaseScheme):
    """Login Response Scheme."""
    access: str
    refresh: str

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....',
                'refresh': 'tg7HJKHG6GKfI1NiIsInR5cCI6IkpHjkgY....',
            }],
        }
    }


class LoginScheme(BaseScheme):
    """Login Scheme."""
    username: str
    password: str
    remember_me: bool = False


class RefreshScheme(BaseScheme):
    """Refresh Token Scheme."""
    refresh: str

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'refresh': 'tg7HJKHG6GKfI1NiIsInR5cCI6IkpHjkgY....',
                },
            ],
        }
    }
