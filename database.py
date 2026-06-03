import os
from dotenv import load_dotenv
from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

load_dotenv()
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
    role: Mapped[str] = mapped_column(String(50), default="User")  # Новое поле для ролей

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user_phone(user_id: int) -> str | None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.phone_number if user else None

async def get_user_role(user_id: int) -> str:
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user.role if user else "User"

async def save_user(user_id: int, username: str | None, first_name: str, phone: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.username = username
            user.first_name = first_name
            user.phone_number = phone
        else:
            new_user = User(user_id=user_id, username=username, first_name=first_name, phone_number=phone, role="User")
            session.add(new_user)
        await session.commit()

async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def update_user_role(user_id: int, new_role: str) -> bool:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.role = new_role
            await session.commit()
            return True
        return False
