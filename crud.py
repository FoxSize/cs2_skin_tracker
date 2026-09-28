import asyncio
from sqlalchemy import select
from databace import async_session_maker
from models import Skin, PriceHistory
from logger import FoxLogger

async def add_skin_price(market_hash_name: str, weapon_type: str, price: float, marketplace:str, exterior:str):
    # Функция создания записи (Upsert логика).
    # Если скин уже есть в базе — добавляет только новую цену в историю.
    # Если скина нет — создает его и добавляет первую цену.
    async with async_session_maker() as session:
        # Ищем скин по его уникальному имени
        stmt = select(Skin).where(Skin.market_hash_name == market_hash_name)
        result = await session.execute(stmt)
        skin = result.scalar_one_or_none()

        # Если скина в БД еще нет, создаем его "профиль"
        if not skin:
            skin = Skin(
                market_hash_name=market_hash_name,
                weapon_type=weapon_type,
                exterior=exterior
            )
            session.add(skin)
            # flush прокидывает данные в БД, чтобы получить ID созданного скина, не делая полный коммит
            await session.flush() 

        # Создаем слепок цены и привязываем его к ID скина
        new_price = PriceHistory(
            skin_id=skin.id,
            price=price,
            marketplace=marketplace
        )
        session.add(new_price)

        # Сохраняем все изменения транзакции
        await session.commit()
        FoxLogger.success("DB", f"Записано: {market_hash_name} -> {price}₽")

async def main():
    # Тестовый запуск для проверки работоспособности БД
    FoxLogger.info("Test", "Запуск тестовых записей в БД...")
    await add_skin_price("AK-47 | Redline (Field-Tested)", "AK-47", 15.50, "Steam", "Field-Tested")
    await add_skin_price("AK-47 | Redline (Field-Tested)", "AK-47", 14.80, "Buff", "Field-Tested")

if __name__ == "__main__":
    asyncio.run(main())
