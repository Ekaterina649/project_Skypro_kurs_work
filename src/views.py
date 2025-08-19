import logging
from datetime import datetime
from typing import Any, Dict

from src.config import DATA_DIR, LOGS_DIR
from src.utils import (
    get_cards_summary,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_time_based_greeting,
    get_top_transactions,
    load_user_settings,
    reader_from_excel,
)

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
        # Загружаем все транзакции
        filepath = DATA_DIR / "operations.xlsx"
        transactions = reader_from_excel(filepath)

        # Преобразуем дату в формат "DD.MM.YYYY HH:MM:SS"
        date_for_filter = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")

        # Приветствие
        greeting_user = get_time_based_greeting(date_for_filter)

        # Фильтрация транзакций
        filtered_transactions = get_greeting(transactions, date_for_filter)

        # Если за выбранный период нет данных
        if not filtered_transactions:
            return {
                "greeting": greeting_user,
                "message": f"За выбранный период ({date_for_filter}) транзакций не найдено.",
            }

        # Считаем сводку по картам
        cards_summary = get_cards_summary(filtered_transactions)

        # Топ-5 расходов
        top_transactions = get_top_transactions(filtered_transactions)

        # Настройки пользователя
        user_settings = load_user_settings()

        # Курсы валют
        currency_rates = get_currency_rates(user_settings)

        # Цены акций
        stock_prices = get_stock_prices(user_settings)

        # Собираем результат
        result = {
            "greeting": greeting_user,
            "cards": cards_summary,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        logger.debug(f"JSON-ответ: {result}")
        return result

    except Exception as e:
        logger.error(f"Ошибка в main_page: {str(e)}")
        return {"error": str(e)}
