from pydantic import BaseModel
from typing import Optional

# Pydantic модели используются для жесткой типизации и валидации "грязных" данных из интернета.
# Если API отдаст строку вместо числа в цене, Pydantic выбросит ошибку до попадания в БД.

class PriceData(BaseModel):
    # Ожидаем цену продажи. Если её нет в ответе, ставим 0.0 по дефолту
    sellPrice: float = 0.0

class SkinItem(BaseModel):
    # Схема для парсинга одного предмета из ответа GraphQL.
    marketHashName: str
    exterior: Optional[str] = "Unknown"
    # Цена может прийти пустой (None), поэтому используем Optional
    price: Optional[PriceData] = None
