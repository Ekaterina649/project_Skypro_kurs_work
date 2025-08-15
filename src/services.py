import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from config import DATA_DIR, LOGS_DIR
from utils import reader_from_excel

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGS_DIR / "services.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """Анализирует выгодность категорий повышенного кешбэка за указанный месяц и год."""
    logger.debug(f"Начало анализа кешбэка за {month}.{year}. Всего транзакций: {len(data)}")
    cashback_by_category = {}
    for transaction in data:
        # Пропускаем транзакции без кешбэка или с нулевым кешбэком
        cashback = transaction.get("Бонусы (включая кэшбэк)")
        if cashback is None or cashback == 0:
            continue

        try:
            op_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
        except (KeyError, ValueError) as e:
            logger.warning(f"Ошибка парсинга даты в транзакции: {transaction.get('Описание')}. Ошибка: {e}")
            continue

        # Проверяем, что транзакция в нужном году и месяце
        if op_date.year != year or op_date.month != month:
            continue

        category = transaction.get("Категория")
        if not category:
            continue

        # Суммируем кешбэк по категориям
        if category in cashback_by_category:
            cashback_by_category[category] += cashback
        else:
            cashback_by_category[category] = cashback

    logger.info("Анализ завершен")
    return json.dumps(cashback_by_category, ensure_ascii=False)


def search_transactions(data: List[Dict[str, Any]], search_query: str) -> str:
    """
    Ищет транзакции, содержащие указанный запрос в описании или категории.
    """
    logger.debug(f"Начало поиска по запросу '{search_query}'. Всего транзакций: {len(data)}")
    results = []
    search_lower = search_query.lower()
    found_count = 0

    for transaction in data:
        description = str(transaction.get("Описание", "")).lower()
        category = str(transaction.get("Категория", "")).lower()

        if search_lower in description or search_lower in category:
            results.append(transaction)
            found_count += 1
    logger.info(f"Поиск завершен. Найдено совпадений: {found_count}")
    return json.dumps(results, ensure_ascii=False, default=str)


filepath = DATA_DIR / "operations.xlsx"
transactions = reader_from_excel(filepath)
file = analyze_cashback_categories(transactions, 2018, 1)
trans = search_transactions(transactions, "Топливо")
print(file)
print(trans)
