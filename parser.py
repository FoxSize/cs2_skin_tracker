import asyncio
import aiohttp
from crud import add_skin_price
from schemas import SkinItem
from logger import FoxLogger

AIM_GRAPHQL_URL = "https://aim.market/v1/api/graphql"

async def parse_aim_market():
    # Основной воркер. Стучится в закрытое API, обходит защиту по User-Agent,
    # вытаскивает JSON, прогоняет через валидатор Pydantic и отдает в БД.
    FoxLogger.info("Parser", "Инициализация парсера aim.market...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Сырой GraphQL запрос. Ищем только нужные поля, чтобы не грузить сеть лишним мусором
    graphql_query = '''
    query ApiBotsInventory($where: BotsInventoryWhereInput, $limit: Int, $order_by: BotsInventorySortInput, $currency: CurrencySymbolEnum, $cursor: BotsInventoryCursor, $language: SteamItemLocaleEnum, $includeLocale: Boolean! = false, $group: Boolean) {
      bots_inventory(where: $where, group: $group, limit: $limit, order_by: $order_by, cursor: $cursor, currency: $currency) {
        items {
          ...BotSteamItem
          locale(language: $language) @include(if: $includeLocale) {
            __typename
          }
        }
        __typename
      }
    }
    fragment BotSteamItem on BotSteamItem {
      id
      appId
      marketHashName
      exterior
      price { sellPrice }
      __typename
    }
    '''

    payload = {
        "operationName": "ApiBotsInventory",
        "query": graphql_query,
        "variables": {
            "currency": "RUB", "limit": 50, "group": True,
            "includeLocale": True, "language": "ru",
            "order_by": {"sellPrice": "desc"},
            "where": {"appId": {"_eq": 730}} # 730 = AppID игры CS2 в Steam
        }
    }

    # Асинхронная сессия позволяет делать запросы не блокируя основной поток выполнения
    async with aiohttp.ClientSession() as session:
        async with session.post(AIM_GRAPHQL_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
               
                # Обработка внутренних ошибок GraphQL (когда статус 200, но в ответе ошибка)
                if "errors" in data:
                    FoxLogger.error("GraphQL", data['errors'][0].get('message', 'Неизвестная ошибка'))
                    return

                # Безопасное извлечение данных без риска словить KeyError
                api_data = data.get("data") or {}
                bots_inventory = api_data.get("bots_inventory") or {}
                items = bots_inventory.get("items") or []

                FoxLogger.success("Parser", f"Пейлоад получен. Обнаружено скинов: {len(items)}")
                
                for raw_item in items:
                    # Валидация сырого словаря через Pydantic схему
                    skin = SkinItem(**raw_item)

                    # Записываем в базу только те предметы, у которых цена больше нуля
                    if skin.price and skin.price.sellPrice > 0:
                        market_name = skin.marketHashName
                        price = skin.price.sellPrice
                        exterior = skin.exterior or "Unknown"
                        weapon_type = market_name.split(" | ")[0] if " | " in market_name else "Unknown"

                        await add_skin_price(market_name, weapon_type, price, "aim.market", exterior)

            else:
                FoxLogger.error("Network", f"Отказ сервера. HTTP Код: {response.status}")


async def main():
    FoxLogger.info("System", "=== Старт работы пайплайна ===")
    await parse_aim_market()
    FoxLogger.info("System", "=== Сбор данных завершен ===")

if __name__ == "__main__":
    asyncio.run(main())
