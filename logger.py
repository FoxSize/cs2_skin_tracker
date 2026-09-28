from datetime import datetime

class FoxLogger:
    """
    Кастомный логгер с паттерном Kitsune.
    Оставляет цифровой след автора и делает вывод в консоль читаемым и профессиональным.
    """
    # Наш уникальный тег-водяной знак
    PREFIX = "<Ktsn>" 

    @staticmethod
    def info(module: str, message: str):
        """Информационные сообщения (запуск, статус)"""
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"{time_now} | {FoxLogger.PREFIX} [{module}] {message}")
    
    @staticmethod
    def error(module: str, message: str):
        """Ошибки (отказы сети, сбои БД)"""
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"{time_now} | {FoxLogger.PREFIX} [ERR::{module}] {message}")
    
    @staticmethod
    def success(module: str, message: str):
        """Успешные действия (запись в базу, успешный парсинг)"""
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"{time_now} | {FoxLogger.PREFIX} [+{module}] {message}")
