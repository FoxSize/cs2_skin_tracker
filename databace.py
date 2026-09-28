import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base
from logger import FoxLogger

# Строка подключения к PostgreSQL. Используем асинхронный драйвер asyncpg для высокой скорости
DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5433/kitsune_db"

# Создаем "движок" базы данных. echo=False отключает спам сырых SQL-запросов в консоль
engine = create_async_engine(DATABASE_URL, echo=False)

# Фабрика сессий. expire_on_commit=False нужен, чтобы объекты не "протухали" после коммита,
# и мы могли обращаться к их атрибутам вне сессии.
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    # Функция для инициализации базы данных.
    # При запуске проверяет модели и создает таблицы, если их еще нет.
    FoxLogger.info("Database", "Подключение к БД и проверка таблиц...")
    async with engine.begin() as conn:
        # Синхронизируем метадату SQLAlchemy с реальной базой
        await conn.run_sync(Base.metadata.create_all)
    FoxLogger.success("Database", "Таблицы успешно инициализированы!")

if __name__ == "__main__":
    # Запускаем инициализацию, если файл вызван напрямую
    asyncio.run(init_db())
