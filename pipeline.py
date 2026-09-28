import asyncio
from logger import FoxLogger
from databace import init_db
from parser import parse_aim_market
from analytics import run_analytics

async def run_pipeline():
    # Главная функция-оркестратор. 
    # Она берет на себя рутину, чтобы тебе не приходилось запускать файлы по одному.
    FoxLogger.info("Pipeline", "=== СТАРТ АВТОМАТИЗИРОВАННОГО ETL-ПАЙПЛАЙНА ===")
    
    FoxLogger.info("Pipeline", "[Шаг 1/3] Проверка и инициализация базы данных...")
    # Ждем, пока таблицы создадутся (если их нет)
    await init_db()
    print("-" * 50)
    
    FoxLogger.info("Pipeline", "[Шаг 2/3] Сбор свежих данных (Extraction & Load)...")
    # Идем на aim.market и закидываем данные в базу
    await parse_aim_market()
    print("-" * 50)
    
    FoxLogger.info("Pipeline", "[Шаг 3/3] Запуск SQL-аналитики (Transformation)...")
    # Делаем тяжелые запросы к БД и выводим результаты
    await run_analytics()
    print("-" * 50)
    
    FoxLogger.success("Pipeline", "=== ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН ===")

if __name__ == "__main__":
    # Запускаем весь процесс одной командой
    asyncio.run(run_pipeline())
