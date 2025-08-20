from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from src.views import main_views


@pytest.fixture
def mock_transactions() -> List[Dict[str, Any]]:
    return [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Номер карты": "1234567890123456",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятёрочка",
            "Статус": "OK",
        }
    ]


@pytest.fixture
def mock_user_settings() -> Dict[str, List[str]]:
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"],
    }


@patch("src.views.load_user_settings")
@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.get_top_transactions")
@patch("src.views.get_cards_summary")
@patch("src.views.get_greeting")
@patch("src.views.get_time_based_greeting")
@patch("src.views.reader_from_excel")
def test_main_views_success(
    mock_reader: Any,
    mock_greeting: Any,
    mock_filter: Any,
    mock_cards: Any,
    mock_top: Any,
    mock_rates: Any,
    mock_stocks: Any,
    mock_settings: Any,
    mock_transactions: List[Dict[str, Any]],
    mock_user_settings: Dict[str, List[str]],
) -> None:
    # Настраиваем моки
    mock_reader.return_value = mock_transactions
    mock_greeting.return_value = "Добрый день"
    mock_filter.return_value = mock_transactions
    mock_cards.return_value = [{"last_digits": "3456", "total_spent": 1000.0, "cashback": 10.0}]
    mock_top.return_value = [{"amount": 1000.0, "category": "Супермаркеты"}]
    mock_rates.return_value = [{"currency": "USD", "rate": 75.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]
    mock_settings.return_value = mock_user_settings

    # Вызываем тестируемую функцию
    result = main_views("2023-01-01 12:00:00")

    # Проверяем результаты
    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "3456"
    assert len(result["top_transactions"]) == 1
    assert result["top_transactions"][0]["amount"] == 1000.0
    assert len(result["currency_rates"]) == 1
    assert result["currency_rates"][0]["currency"] == "USD"
    assert len(result["stock_prices"]) == 1
    assert result["stock_prices"][0]["stock"] == "AAPL"
