from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Базовый класс, от которого наследуются все таблицы
class Base(DeclarativeBase):
    pass

class Skin(Base):
    # Таблица для хранения уникальных скинов.
    # Мы нормализуем БД: храним название предмета здесь, а историю его цен - в другой таблице.
    __tablename__ = "skins"

    id: Mapped[int] = mapped_column(primary_key=True)
    # market_hash_name уникален, по нему мы ищем скин. Индекс ускоряет поиск.
    market_hash_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    weapon_type: Mapped[str] = mapped_column(String(50))
    exterior: Mapped[str] = mapped_column(String(50))

    # Связь "Один ко многим" с таблицей цен. Если удалить скин, удалятся и его цены (cascade)
    prices: Mapped[list["PriceHistory"]] = relationship(
            back_populates="skin",
            cascade="all, delete-orphan"
    )

class PriceHistory(Base):
    # Таблица временных рядов (Time-Series) для истории цен.
    # Позволяет отслеживать, как менялась цена на один и тот же скин со временем.
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Внешний ключ, связывающий цену с конкретным скином
    skin_id: Mapped[int] = mapped_column(ForeignKey("skins.id"), index=True)
    price: Mapped[float] = mapped_column(Float)
    marketplace: Mapped[str] = mapped_column(String(50))
    # Автоматически ставим время записи. Полезно для аналитики и графиков.
    parsed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Обратная связь с таблицей Skin
    skin: Mapped["Skin"] = relationship(back_populates="prices")
