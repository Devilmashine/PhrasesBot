from db import User, async_session
from sqlalchemy import select


async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        user = result.scalars().first()  # Get the first row
        return user
