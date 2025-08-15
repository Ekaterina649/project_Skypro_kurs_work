from unittest.mock import patch, Mock

import pandas as pd
import pytest

from src.utils import (
    get_time_based_greeting,
    get_greeting,
    get_cards_summary,
    get_top_transactions,
    get_stock_prices,
    get_currency_rates,
    reader_from_excel,
)


@pytest.fixture
def sample_excel_file(tmp_path):
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
    return file_path


def test_reader_from_excel(sample_excel_file):
    """Тест чтения Excel-файла."""
    result = reader_from_excel(sample_excel_file)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["Дата операции"] == "01.01.2023 12:00:00"


@pytest.fixture
def sample_transactions():
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
def test_get_time_based_greeting(date_str, expected_greeting):
    """Тест приветствия в зависимости от времени."""
    assert get_time_based_greeting(date_str) == expected_greeting


def test_get_greeting(sample_transactions):
    """Тест фильтрации транзакций по дате."""
    date_str = "10.01.2023 00:00:00"
    result = get_greeting(sample_transactions, date_str)
    assert len(result) == 2


def test_get_cards_summary(sample_transactions):
    """Тест формирования сводки по картам."""
    result = get_cards_summary(sample_transactions)
    assert len(result) == 2
    assert result[0]["last_digits"] == "1234567890123456"
    assert result[0]["total_spent"] == 1000.0
    assert result[0]["cashback"] == 10.0


def test_get_top_transactions(sample_transactions):
    """Тест получения топ-5 транзакций."""
    result = get_top_transactions(sample_transactions)
    assert len(result) == 2
    assert result[0]["amount"] == 1000.0
    assert result[1]["amount"] == 500.0


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get):
    """Тест получения курсов валют с моком API."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "quotes": {"RUBUSD": 0.013, "RUBEUR": 0.011},
    }
    mock_get.return_value = mock_response

    with patch("src.utils.SETTINGS_PATH", "dummy_path"):  # Исправлен путь
        result = get_currency_rates({"user_currencies": ["USD", "EUR"]})

    assert len(result) == 2
    assert result[0]["currency"] == "EUR"
    assert result[0]["rate"] == round(1 / 0.011, 2)
    assert result[1]["currency"] == "USD"
    assert result[1]["rate"] == round(1 / 0.013, 2)


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get):
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
