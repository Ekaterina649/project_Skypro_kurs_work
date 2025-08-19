import json

import pandas as pd
import pytest

from src.reports import save_report, spending_by_category


@pytest.fixture
def transactions_df():
    """Создаем тестовый DataFrame с транзакциями."""
    data = [
        {
            "Дата операции": "10.01.2018 21:31:46",
            "Сумма платежа": -100,
            "Кэшбэк": 5,
            "Описание": "Оплата сада",
            "Категория": "Детский сад",
            "Статус": "OK",
        },
        {
            "Дата операции": "15.01.2018 10:00:00",
            "Сумма платежа": -50,
            "Кэшбэк": None,
            "Описание": "Заправка",
            "Категория": "Топливо",
            "Статус": "OK",
        },
        {
            "Дата операции": "01.02.2018 12:00:00",
            "Сумма платежа": 200,
            "Кэшбэк": 10,
            "Описание": "Пополнение",
            "Категория": "Другое",
            "Статус": "OK",
        },
        {
            "Дата операции": "05.01.2018 08:00:00",
            "Сумма платежа": -30,
            "Кэшбэк": 0,
            "Описание": "Канцтовары",
            "Категория": "Детский сад",
            "Статус": "OK",
        },
        {
            "Дата операции": "20.12.2017 08:00:00",
            "Сумма платежа": -20,
            "Кэшбэк": 0,
            "Описание": "Игрушки",
            "Категория": "Детский сад",
            "Статус": "OK",
        },
    ]
    df = pd.DataFrame(data)
    # Приводим колонку "Дата операции" к datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return df


def test_transactions_found(transactions_df):
    """Проверяем, что транзакции возвращаются корректно, если они есть."""
    result = spending_by_category(transactions_df, "Детский сад", "10.01.2018 21:31:46")
    assert len(result) == 3


def test_transactions_not_found(transactions_df):
    """Проверяем, что возвращается сообщение при отсутствии транзакций."""
    result = spending_by_category(transactions_df, "Еда", "10.01.2018 21:31:46")

    assert isinstance(result, str)
    assert "не найдены" in result


def test_empty_dataframe():
    """Проверяем поведение на пустом DataFrame."""
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Кэшбэк", "Описание", "Категория", "Статус"])
    result = spending_by_category(empty_df, "Детский сад", "10.01.2018 21:31:46")

    assert isinstance(result, str)
    assert "не найдены" in result


@pytest.fixture
def sample_df():
    data = [
        {
            "Дата операции": "01.01.2023 12:00:00",
            "Сумма платежа": -100,
            "Кэшбэк": 5,
            "Описание": "Тест",
            "Категория": "Тест",
            "Статус": "OK",
        },
    ]
    return pd.DataFrame(data)


def test_save_report_creates_file(tmp_path, sample_df):
    """Проверяем, что декоратор создает JSON-файл и записывает данные."""

    test_file = tmp_path / "test_report.json"

    @save_report(filename=test_file)
    def dummy_report():
        return sample_df

    result = dummy_report()
    # Проверяем, что возвращается DataFrame
    pd.testing.assert_frame_equal(result, sample_df)

    # Проверяем, что файл создан
    assert test_file.exists()

    # Проверяем содержимое файла
    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["Сумма платежа"] == -100
