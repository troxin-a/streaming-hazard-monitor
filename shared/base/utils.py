from typing import NoReturn

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status


def get_error_message(err: IntegrityError, conflict: bool = False) -> str:
    """Get error massage."""
    *_, error_msg = f'{err.orig}'.split(':')
    if conflict:
        *_, error_msg = f'{err.orig}'.split('\n')[0].split(':')
    error = error_msg.strip().replace(')', '').replace('(', '').replace('"', '')
    return error


def handle_error(error: IntegrityError) -> NoReturn:
    """Handle error message."""
    error_text = get_error_message(error)
    if 'not present in table' in error_text or 'FOREIGN KEY' in error_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_text)
    error_text = get_error_message(error, True)
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_text)
