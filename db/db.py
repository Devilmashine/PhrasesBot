from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import config

engine = create_async_engine(
    config.sqlalchemy_url.get_secret_value(),
    echo=True
)

async_session = async_sessionmaker(
    engine
)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    tg_id = mapped_column(BigInteger)
    openai_token = mapped_column(String)  # Use String type for the openai_token column
    tg_username: Mapped[str] = mapped_column(String)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def register_user(tg_id: BigInteger, tg_username: str) -> None:
    async with async_session() as session:
        user = User(tg_id=tg_id, tg_username=tg_username)
        session.add(user)
        await session.commit()

async def add_or_update_openai_token(tg_id: BigInteger, openai_token: str) -> None:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        user.openai_token = openai_token
        session.update(user)
        await session.commit()

async def change_is_banned_status(tg_id: BigInteger, is_banned: bool) -> None:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        user.is_banned = is_banned
        session.update(user)
        await session.commit()

async def change_is_admin_status(tg_id: BigInteger, is_admin: bool) -> None:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        user.is_admin = is_admin
        session.update(user)
        await session.commit()

async def get_is_banned_status(tg_id: BigInteger) -> bool:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        return user.is_banned

async def get_is_admin_status(tg_id: BigInteger) -> bool:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        return user.is_admin

async def get_openai_token(tg_id: BigInteger) -> str:
    async with async_session() as session:
        user = await session.get(User, tg_id)
        return user.openai_token
