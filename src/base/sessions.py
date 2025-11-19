from sqlalchemy.ext.asyncio import AsyncSession


class BaseSession:
    """Base session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
