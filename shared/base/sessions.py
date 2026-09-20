from sqlalchemy import Executable, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.base.utils import handle_error


class BaseSession:
    """Base session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def flush(self) -> None:
        """Flush pending changes, turning an integrity error into an http error."""
        try:
            await self.session.flush()
        except IntegrityError as err:
            handle_error(err)

    async def execute(self, statement: Executable) -> Result:
        """Execute statement, turning an integrity error into an http error."""
        try:
            return await self.session.execute(statement)
        except IntegrityError as err:
            handle_error(err)
