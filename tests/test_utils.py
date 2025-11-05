from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (get_cards_summary, get_currency_rates, get_greeting, get_stock_prices, get_time_based_greeting,
                       get_top_transactions, reader_from_excel)


@pytest.fixture
def sample_excel_file(tmp_path: Any) -> str:
    """Создает временный Excel-файл с тестовыми данными."""
    data = [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятёрочка",
            "Статус": "OK",
        },
        {
            "Дата операции": "05.01.2023 18:00:00",
            "Номер карты": "9876543210987654",
            "Сумма платежа": -500.0,
            "Категория": "Топливо",
            "Описание": "АЗС",
            "Статус": "OK",
        },
        {
            "Дата операции": "10.01.2023 09:00:00",
            "Номер карты": None,
            "Сумма платежа": 2000.0,
            "Категория": "Пополнения",
            "Описание": "Перевод",
            "Статус": "OK",
        },
    ]
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_operations.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")
    return str(file_path)


def test_reader_from_excel(sample_excel_file: str) -> None:
    """Тест чтения Excel-файла."""
    result = reader_from_excel(sample_excel_file)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["Дата операции"] == "01.01.2023 12:00:00"


def test_reader_from_excel_empty_file(tmp_path: Any) -> None:
    """Тест чтения пустого Excel-файла."""
    file_path = tmp_path / "empty.xlsx"
    df = pd.DataFrame()
    df.to_excel(file_path, index=False, engine="openpyxl")

    result = reader_from_excel(str(file_path))
    assert isinstance(result, list)
    assert len(result) == 0


def test_reader_from_excel_nonexistent_file() -> None:
    """Тест чтения несуществующего файла."""
    with pytest.raises(FileNotFoundError):
        reader_from_excel("nonexistent_file.xlsx")


def test_get_time_based_greeting_invalid_format() -> None:
    """Тест приветствия с неверным форматом даты."""
    result = get_time_based_greeting("invalid_date")
    assert result == "Добрый день"


def test_get_greeting_empty_transactions() -> None:
    """Тест фильтрации пустого списка транзакций."""
    result = get_greeting([], "01.01.2023 12:00:00")
    assert len(result) == 0


def test_get_greeting_no_matching_dates() -> None:
    """Тест фильтрации, когда нет подходящих дат."""
    transactions = [
        {
            "Дата операции": "01.02.2023 12:00:00",  # Февраль, а фильтруем январь
            "Сумма платежа": -1000.0,
            "Статус": "OK",
        }
    ]

    result = get_greeting(transactions, "31.01.2023 23:59:59")
    assert len(result) == 0


def test_get_cards_summary_empty() -> None:
    """Тест сводки по картам с пустым списком."""
    result = get_cards_summary([])
    assert len(result) == 0


def test_get_cards_summary_skip_non_ok_status() -> None:
    """Тест пропуска транзакций со статусом не OK."""
    transactions = [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Статус": "PENDING",
        }
    ]

    result = get_cards_summary(transactions)
    assert len(result) == 0


def test_get_cards_summary_no_card_number() -> None:
    """Тест пропуска транзакций без номера карты."""
    transactions = [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Номер карты": None,
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Статус": "OK",
        }
    ]

    result = get_cards_summary(transactions)
    assert len(result) == 0


def test_get_currency_rates_only_rub() -> None:
    """Тест получения курсов, когда указан только RUB."""
    result = get_currency_rates({"user_currencies": ["RUB"]})
    assert len(result) == 1
    assert result[0]["currency"] == "RUB"
    assert result[0]["rate"] == 1.0


@patch("src.utils.requests.get")
def test_get_stock_prices_empty_stocks(mock_get: Mock) -> None:
    """Тест получения цен акций без указания акций."""
    result = get_stock_prices({})
    assert len(result) == 0
    mock_get.assert_not_called()


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Возвращает список тестовых транзакций."""
    return [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятёрочка",
            "Статус": "OK",
        },
        {
            "Дата операции": "05.01.2023 18:00:00",
            "Номер карты": "9876543210987654",
            "Сумма платежа": 500.0,
            "Категория": "Топливо",
            "Описание": "АЗС",
            "Статус": "OK",
        },
    ]


@pytest.mark.parametrize(
    "date_str, expected_greeting",
    [
        ("01.01.2023 06:00:00", "Доброе утро"),
        ("01.01.2023 14:00:00", "Добрый день"),
        ("01.01.2023 20:00:00", "Добрый вечер"),
        ("01.01.2023 02:00:00", "Доброй ночи"),
    ],
)
def test_get_time_based_greeting(date_str: str, expected_greeting: str) -> None:
    """Тест приветствия в зависимости от времени."""
    assert get_time_based_greeting(date_str) == expected_greeting


def test_get_greeting(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации транзакций по дате."""
    date_str = "10.01.2023 00:00:00"
    result = get_greeting(sample_transactions, date_str)
    assert len(result) == 2


def test_get_cards_summary(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест формирования сводки по картам."""
    result = get_cards_summary(sample_transactions)
    assert len(result) == 2
    assert result[0]["last_digits"] == "1234567890123456"
    assert result[0]["total_spent"] == 1000.0
    assert result[0]["cashback"] == 10.0


def test_get_top_transactions(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест получения топ-5 транзакций."""
    result = get_top_transactions(sample_transactions)
    assert len(result) == 2
    assert result[0]["amount"] == 1000.0
    assert result[1]["amount"] == 500.0


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get: Mock) -> None:
    """Тест получения курсов валют с моком API."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "quotes": {"RUBUSD": 0.013, "RUBEUR": 0.011},
    }
    mock_get.return_value = mock_response

    with patch("src.utils.SETTINGS_PATH", "dummy_path"):
        result = get_currency_rates({"user_currencies": ["USD", "EUR"]})
    assert len(result) == 3
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] == round(1 / 0.011, 2)
    assert result[1]["currency"] == "RUB"
    assert result[1]["rate"] == 1.0
    assert result[2]["currency"] == "USD"
    assert result[2]["rate"] == round(1 / 0.013, 2)


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get: Mock) -> None:
    """Тест получения цен акций с моком API."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "Time Series (5min)": {
            "2023-01-01 15:00:00": {"4. close": "150.50"},
        }
    }
    mock_get.return_value = mock_response

    with patch("src.utils.SETTINGS_PATH", "dummy_path"):
        result = get_stock_prices({"user_stocks": ["AAPL"]})

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.50
