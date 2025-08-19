import json
import logging
from functools import wraps
from pathlib import Path
from typing import Optional, Any

import pandas as pd

from src.config import LOGS_DIR, DATA_DIR
from src.utils import reader_from_excel

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGS_DIR / "reports.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def save_report(filename: Optional[str] = None):
    """Декоратор для сохранения результата функции отчета в JSON-файл."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            report_filename = Path(__file__).resolve().parent.parent / filename if filename \
                else Path(__file__).resolve().parent.parent / f"{func.__name__}.json"
            try:
                if isinstance(result, pd.DataFrame):
                    with open(report_filename, "w", encoding="utf-8") as f:
                        json.dump(
                            json.loads(result.to_json(orient="records", force_ascii=False)),
                            f, ensure_ascii=False, indent=2
                        )
                else:
                    with open(report_filename, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчет сохранен: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета {report_filename}: {e}")

            return result
        return wrapper

    return decorator

@save_report()
def spending_by_category(transactions: pd.DataFrame,category: str, date: Optional[str] = None) -> str | Any:
    """Возвращает траты по категории за последние 3 месяца от переданной даты."""
    if date is None:
        end_date = pd.Timestamp.today().normalize()
    else:
        end_date = pd.to_datetime(date)

    start_date = end_date - pd.DateOffset(months=3)
    logger.debug(f"Фильтрация транзакций: {start_date.date()} - {end_date.date()}, категория={category}")

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    df["Кэшбэк"] = df["Кэшбэк"].fillna(0)

    mask = (
            (df["Дата операции"] >= start_date) &
            (df["Дата операции"] <= end_date) &
            (df["Категория"] == category) &
            (df["Сумма платежа"] < 0) &
            (df["Статус"] == "OK")
    )
    filtered = df.loc[mask, ["Дата операции", "Сумма платежа", "Кэшбэк", "Описание"]]
    if filtered.empty:
        message = f"Транзакции по категории '{category}' за период {start_date.date()} - {end_date.date()} не найдены."
        logger.warning(message)
        return message

    logger.debug(f"Найдено {len(filtered)} транзакций по категории '{category}'")
    return filtered

filepath = DATA_DIR / "operations.xlsx"
transactions = reader_from_excel(filepath)
df = pd.DataFrame(transactions)
report = spending_by_category(df,"Детский сад","10.01.2018 21:31:46")
print(report)