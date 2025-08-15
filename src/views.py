import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config import DATA_DIR, LOGS_DIR
from utils import reader_from_excel, get_greeting, get_cards_summary, get_top_transactions, load_user_settings, \
    get_currency_rates, get_stock_prices, get_time_based_greeting

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGS_DIR / "views.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main_views(date_str: str) -> Dict[str, Any]:
    """
    Главная страница: собирает данные по транзакциям, картам, валютам и акциям.
    :param date_str: Дата в формате YYYY-MM-DD HH:MM:SS
    :return: JSON-ответ (dict)
    """
    try:
        # 1. Загружаем все транзакции
        filepath = DATA_DIR / "operations.xlsx"
        transactions = reader_from_excel(filepath)

        # 2. Фильтруем по дате и выводим приветствие
        # преобразуем дату в формат "DD.MM.YYYY HH:MM:SS", чтобы get_greeting понимала
        date_for_filter = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
        greeting_user = get_time_based_greeting(date_for_filter)
        filtered_transactions = get_greeting(transactions, date_for_filter)

        # 3. Считаем сводку по картам
        cards_summary = get_cards_summary(filtered_transactions)

        # 4. Определяем топ-5 расходов
        top_transactions = get_top_transactions(filtered_transactions)

        # 5. Загружаем настройки пользователя
        user_settings = load_user_settings()

        # 6. Получаем курсы валют
        currency_rates = get_currency_rates(user_settings)

        # 7. Получаем цены акций
        stock_prices = get_stock_prices(user_settings)

        # 8. Собираем результат
        result = {
            "greeting": greeting_user,
            "cards": cards_summary,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        logger.debug(f"JSON-ответ: {result}")
        return result

    except Exception as e:
        logger.error(f"Ошибка в main_page: {str(e)}")
        return {"error": str(e)}

