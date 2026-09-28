🦊 CS2 Market ETL Pipeline & Analytics

📌 О проекте

Асинхронный ETL-пайплайн (Extract, Transform, Load) для сбора, хранения и аналитики рыночных цен на виртуальные предметы (скины) из игры CS2. Проект демонстрирует навыки работы со скрытыми GraphQL API, асинхронным программированием, нормализацией реляционных баз данных и написанием сложных SQL-запросов.

🛠 Технический стек

Язык: Python 3.11+

База данных: PostgreSQL 15 (развернута в Docker)

ORM & SQL: SQLAlchemy 2.0 (asyncpg)

Асинхронность: asyncio, aiohttp

Валидация данных: Pydantic

Оркестрация: Кастомный Python-оркестратор (pipeline.py)

⚙️ Архитектура системы (ETL)

Extract (Парсинг):
Модуль parser.py обходит защиту по User-Agent и отправляет точечные GraphQL-запросы к закрытому API маркетплейса, получая JSON-ответы. Данные строго типизируются на лету через Pydantic.

Load (Загрузка в БД):
Модуль crud.py использует стратегию "Upsert". База данных нормализована (1NF-3NF): названия скинов и история их цен разнесены по разным таблицам (skins и price_history), связанных отношением One-to-Many.

Transform & Analytics (SQL-аналитика):
Модуль analytics.py выполняет "сырые" SQL-запросы к PostgreSQL, демонстрируя работу с:

Связями таблиц (JOIN)

Группировками и агрегацией (GROUP BY, COUNT, AVG, MAX)

Оконными функциями (RANK() OVER PARTITION BY)

Обобщенными табличными выражениями и подзапросами (CTE)

🚀 Быстрый старт

1. Клонирование и настройка окружения

git clone https://github.com/ВАШ_НИК/cs2_skin_tracker.git
cd cs2_skin_tracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


2. Запуск базы данных

# Поднимаем PostgreSQL в фоновом режиме
sudo docker compose up -d


3. Запуск ETL-пайплайна

# Оркестратор сам инициализирует таблицы, соберет данные и выведет аналитику
python pipeline.py


👤 Автор

Разработано с акцентом на отказоустойчивость и чистый код.

Внутренний трекинг-тег системы: <Ktsn>
