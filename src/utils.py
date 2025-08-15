import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import LOGS_DIR, SETTINGS_PATH

load_dotenv()

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGS_DIR / "utils.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def reader_from_excel(filepath):
    """Читает файл Excel и возвращает список транзакций в виде словарей."""
    logger.debug("Чтение файла excel")
    dataframe = pd.read_excel(filepath, engine="openpyxl")
    return dataframe.to_dict("records")


def get_time_based_greeting(date_str: str) -> str:
    """Возвращает приветствие в зависимости от текущего времени."""
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        hour = dt.hour

        if 5 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 17:
            greeting = "Добрый день"
        elif 17 <= hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        logger.debug(f"{dt}-{greeting}")
        return greeting

    except Exception as e:
        logger.error(f"Ошибка в get_time_based_greeting: {str(e)}")
        return "Добрый день"


def get_greeting(transactions: List[Dict[str, Any]], date_str: str) -> List[Dict[str, Any]]:
    """Фильтрует транзакции с начала месяца до указанной даты."""
    date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S").date()
    start_month = date.replace(day=1)  # Первое число месяца

    filtered_transactions = []
    for operation in transactions:
        op_date = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S").date()

        if start_month <= op_date <= date:
            filtered_transactions.append(operation)

    logger.debug(f"Отфильтровано {len(filtered_transactions)} транзакций за период {start_month} - {date}")
    return filtered_transactions


def get_cards_summary(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Возвращает список словарей с суммой расходов и кешбэком по каждой карте."""
    cards = {}
    for operation in transactions:
        if operation.get("Статус") != "OK":
            continue
        if operation.get("Категория") in ("Пополнения", "Переводы"):
            continue
        if operation.get("Номер карты") is None:
            continue
        last_digits = str(operation.get("Номер карты", "???"))
        total_spent = abs(float(operation.get("Сумма платежа", 0)))
        if last_digits not in cards:
            cards[last_digits] = 0
        cards[last_digits] += total_spent
    result = [
        {"last_digits": last_digits, "total_spent": total_spent, "cashback": round(total_spent / 100, 2)}
        for last_digits, total_spent in cards.items()
    ]
    logger.debug(f"Сводка по картам: {result}")
    return result


def get_top_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Возвращает топ-5 транзакций по сумме платежа."""
    df = pd.DataFrame(transactions)
    df = df[df["Статус"] == "OK"]
    df["Абсолютная сумма"] = df["Сумма платежа"].abs()
    df_sorted = df.sort_values(by="Абсолютная сумма", ascending=False).head(5)
    top_operations = []
    for _, transaction in df_sorted.iterrows():
        top_operations.append(
            {
                "date": pd.to_datetime(transaction["Дата операции"]).strftime("%d.%m.%Y"),
                "amount": round(abs(transaction["Сумма платежа"]), 2),
                "category": transaction.get("Категория", ""),
                "description": transaction.get("Описание", ""),
            }
        )
    logger.debug(f"Топ-5 расходов: {top_operations}")
    return top_operations


def load_user_settings() -> Dict[str, List[str]]:
    """Загружает пользовательские настройки из user_settings.json."""
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            settings = json.load(file)
        logger.debug(f"Настройки загружены: {settings}")
        return settings
    except Exception as e:
        logger.error(f"Ошибка при загрузке настроек: {e}")
        return {}


def get_currency_rates(user_settings: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Получает курсы валют в привычном формате (1 USD = X RUB)
    """
    EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL")
    EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

    result = []
    currencies = [c for c in user_settings.get("user_currencies", ["USD", "EUR"]) if c != "RUB"]

    if not currencies:
        return [{"currency": "RUB", "rate": 1.0}]

    try:
        params = {
            "access_key": EXCHANGE_API_KEY,
            "source": "RUB",
            "currencies": ",".join(currencies),
        }

        response = requests.get(EXCHANGE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            quotes = data.get("quotes", {})
            logger.debug(f"Quotes: {quotes}")

            for currency in currencies:
                # Получаем курс вида 1 RUB = X USD (например: 0.0134)
                rub_to_curr = quotes.get(f"RUB{currency}")

                if rub_to_curr:
                    # Конвертируем в 1 USD = Y RUB (1 / 0.0134 ≈ 74.63)
                    curr_to_rub = round(1 / float(rub_to_curr), 2)
                    result.append({"currency": currency, "rate": curr_to_rub})
                else:
                    logger.warning(f"No rate for {currency}")
                    result.append({"currency": currency, "rate": 0.0})
        else:
            logger.error(f"API error: {data.get('error', {}).get('info')}")
            result = [{"currency": c, "rate": 0.0} for c in currencies] + [{"currency": "RUB", "rate": 1.0}]

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        result = [{"currency": c, "rate": 0.0} for c in currencies] + [{"currency": "RUB", "rate": 1.0}]

    logger.info(f"Result: {result}")
    return sorted(result, key=lambda x: x["currency"])


def get_stock_prices(user_stocks: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Получает цены акций с Alpha Vantage."""
    STOCK_API_KEY = os.getenv("STOCK_API_KEY")
    STOCK_API_URL = os.getenv("STOCK_API_URL")

    result = []
    stocks = user_stocks.get("user_stocks", [])

    for symbol in stocks:
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "5min",
                "outputsize": "compact",
                "apikey": STOCK_API_KEY,
            }

            response = requests.get(STOCK_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            time_series = data.get("Time Series (5min)", {})
            if not time_series:
                logger.warning(f"Для акции {symbol} не найдены данные в ответе API")
                continue

            latest_timestamp = max(time_series.keys())
            latest_data = time_series[latest_timestamp]
            latest_price = round(float(latest_data["4. close"]), 2)

            result.append({"stock": symbol, "price": latest_price})

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе акции {symbol}: {str(e)}")
            result.append({"stock": symbol, "price": None})
        except Exception as e:
            logger.error(f"Ошибка {symbol}: {str(e)}")
            result.append({"stock": symbol, "price": None})

    return result
