import json
from typing import Any, Dict, List, Optional

import pytest

from src.services import analyze_cashback_categories, search_transactions


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {
            "Дата операции": "10.01.2018 21:31:46",
            "Категория": "Топливо",
            "Бонусы (включая кэшбэк)": 100,
            "Описание": "АЗС Лукойл",
        },
        {
            "Дата операции": "15.01.2018 12:00:00",
            "Категория": "Супермаркеты",
            "Бонусы (включая кэшбэк)": 50,
            "Описание": "Пятёрочка",
        },
        {
            "Дата операции": "20.02.2018 18:30:00",  # Не подходит по месяцу
            "Категория": "Топливо",
            "Бонусы (включая кэшбэк)": 80,
            "Описание": "АЗС Газпром",
        },
        {
            "Дата операции": "10.01.2018 09:15:00",
            "Категория": None,  # Нет категории
            "Бонусы (включая кэшбэк)": 30,
            "Описание": "Неизвестная операция",
        },
    ]


@pytest.fixture
def empty_transactions() -> List[Dict[str, Any]]:
    return []


@pytest.mark.parametrize(
    "year,month,expected",
    [
        (2018, 1, {"Топливо": 100, "Супермаркеты": 50}),
        (2018, 2, {"Топливо": 80}),
        (2019, 1, None),  # теперь ожидаем None для пустого результата
    ],
)
def test_analyze_cashback_categories(sample_transactions, year, month, expected):
    """Параметризованный тест для analyze_cashback_categories"""
    result = analyze_cashback_categories(sample_transactions, year, month)
    if expected is None:
        assert result is None
    else:
        assert json.loads(result) == expected


def test_analyze_cashback_categories_empty(empty_transactions):
    """Тест с пустыми входными данными"""
    result = analyze_cashback_categories(empty_transactions, 2018, 1)
    assert result is None  # пустой словарь -> None


@pytest.mark.parametrize(
    "query,expected_count,expected_descriptions",
    [
        ("АЗС", 2, ["АЗС Лукойл", "АЗС Газпром"]),
        ("пятёрочка", 1, ["Пятёрочка"]),
        ("", 4, ["АЗС Лукойл", "Пятёрочка", "АЗС Газпром", "Неизвестная операция"]),
        ("Ресторан", 0, []),
    ],
)
def test_search_transactions(sample_transactions, query, expected_count, expected_descriptions):
    """Параметризованный тест для search_transactions"""
    result = search_transactions(sample_transactions, query)
    result_list = json.loads(result)
    assert len(result_list) == expected_count
    assert [t["Описание"] for t in result_list] == expected_descriptions


def test_search_transactions_empty(empty_transactions):
    """Тест поиска с пустыми данными"""
    result = search_transactions(empty_transactions, "АЗС")
    assert json.loads(result) == []
