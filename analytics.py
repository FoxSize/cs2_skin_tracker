import asyncio
from sqlalchemy import text
from databace import async_session_maker
from logger import FoxLogger

async def run_analytics():
    # Модуль аналитики. Выполняет прямые сырые (raw) SQL-запросы к базе данных.
    # Демонстрирует навыки работы с JOIN, GROUP BY, Window Functions и CTE.
    async with async_session_maker() as session:
        
        FoxLogger.info("Analytics", "1. Средняя цена по типам оружия (GROUP BY + JOIN)")
        # Так как цены лежат в отдельной таблице, мы используем JOIN для связи таблиц
        query_agg = text('''
            SELECT s.weapon_type, 
                   COUNT(DISTINCT s.id) as total_unique_skins, 
                   ROUND(AVG(p.price)::numeric, 2) as avg_price, 
                   MAX(p.price) as max_price
            FROM skins s
            JOIN price_history p ON s.id = p.skin_id
            GROUP BY s.weapon_type
            ORDER BY avg_price DESC
            LIMIT 5;
        ''')
        result_agg = await session.execute(query_agg)
        for row in result_agg:
            print(f"Оружие: {row.weapon_type} | Уникальных скинов: {row.total_unique_skins} | Средняя цена: {row.avg_price} ₽")

        print("\n" + "-" * 50)
        FoxLogger.info("Analytics", "2. Топ-3 самых дорогих скинов в каждом качестве (Оконные функции)")
        # Выбираем максимальную цену для каждого уникального скина, чтобы избежать дубликатов из price_history
        query_window = text('''
            WITH RankedSkins AS (
                SELECT s.market_hash_name, 
                       s.exterior, 
                       MAX(p.price) as max_price,
                       RANK() OVER (PARTITION BY s.exterior ORDER BY MAX(p.price) DESC) as rank
                FROM skins s
                JOIN price_history p ON s.id = p.skin_id
                WHERE s.exterior != 'Unknown'
                GROUP BY s.market_hash_name, s.exterior
            )
            SELECT market_hash_name, exterior, max_price as price, rank 
            FROM RankedSkins 
            WHERE rank <= 3;
        ''')
        result_window = await session.execute(query_window)
        for row in result_window:
            print(f"[{row.exterior}] #{row.rank}: {row.market_hash_name} -> {row.price} ₽")

        print("\n" + "-" * 50)
        FoxLogger.info("Analytics", "3. Поиск аномально дорогих скинов (CTE / Подзапросы)")
        # Группируем уникальные предметы перед сравнением со средней ценой по рынку
        query_cte = text('''
            WITH GlobalAvg AS (
                SELECT AVG(price) as avg_price FROM price_history
            ),
            UniqueSkins AS (
                SELECT s.market_hash_name, MAX(p.price) as max_price
                FROM skins s
                JOIN price_history p ON s.id = p.skin_id
                GROUP BY s.market_hash_name
            )
            SELECT u.market_hash_name, u.max_price as price, (SELECT ROUND(avg_price::numeric, 2) FROM GlobalAvg) as global_avg
            FROM UniqueSkins u, GlobalAvg
            WHERE u.max_price > GlobalAvg.avg_price
            ORDER BY u.max_price DESC
            LIMIT 5;
        ''')
        result_cte = await session.execute(query_cte)
        for row in result_cte:
            print(f"Аномалия: {row.market_hash_name} -> {row.price} ₽ (Средняя по рынку: {row.global_avg} ₽)")

if __name__ == "__main__":
    asyncio.run(run_analytics())
