"""Create a superuser."""
import asyncio
import sys
from getpass import getpass

from sqlalchemy import select

from api.auth.services.utils import HashPassword
from shared.config.session import async_session_maker
from shared.user.models import UserDB


def ask(prompt: str) -> str:
    """Ask the value until it is not empty."""
    while not (value := input(prompt).strip()):
        print('Value must not be empty.')
    return value


def ask_password() -> str:
    """Ask the password twice until both are equal and not empty."""
    while True:
        password = getpass('Password: ')
        if not password:
            print('Password must not be empty.')
        elif password != getpass('Password (again): '):
            print('Passwords must be the same.')
        else:
            return password


async def username_exists(username: str) -> bool:
    """Check the user with the username exists."""
    async with async_session_maker() as session:
        return await session.scalar(select(UserDB.uuid).filter_by(username=username)) is not None


async def create_superuser() -> None:
    """Ask the username, name and password and create the superuser."""
    username = ask('Username: ')
    if await username_exists(username):
        sys.exit(f'User {username} already exists.')
    name = ask('Name: ')
    password = ask_password()
    async with async_session_maker() as session, session.begin():
        session.add(UserDB(
            username=username,
            name=name,
            password=HashPassword.hash_password(password),
            is_superuser=True,
        ))
    print(f'Superuser {username} is created.')


if __name__ == '__main__':
    asyncio.run(create_superuser())
