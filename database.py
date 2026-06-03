import os
from dotenv import load_dotenv
from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
# Сейчас: sqlite+aiosqlite:///users.db
# Будет для Postgres: postgresql+asyncpg://user:pass@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///warehouse_bot.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(50))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user_phone(user_id: int) -> str | None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.phone_number if user else None

async def save_user(user_id: int, username: str | None, first_name: str, phone: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.username = username
            user.first_name = first_name
            user.phone_number = phone
        else:
            new_user = User(user_id=user_id, username=username, first_name=first_name, phone_number=phone)
            session.add(new_user)
        await session.commit()
