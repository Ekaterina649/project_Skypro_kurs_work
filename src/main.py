import os
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv

from src.reports import spending_by_category
from src.services import analyze_cashback_categories, search_transactions
from src.user_interaction import (ask_month, ask_year, get_category_input, get_date_input, get_end_date,
                                  get_search_query)
from src.utils import reader_from_excel
from src.views import main_views

load_dotenv()


def show_dashboard(transactions: List[Dict[str, Any]]) -> None:
    """Главная страница: приветствие, карты, топ-5 трат, валюты, акции"""
    while True:
        try:
            time_user = get_date_input("Введите дату (YYYY-MM-DD HH:MM:SS) или Enter для текущей: ")
            result = main_views(time_user)
            print("\n=== Главная страница ===")
            print(result)
            break
        except Exception as e:
            print(f"Ошибка при формировании главной страницы: {e}")
            break


def cashback_analysis(transactions: List[Dict[str, Any]]) -> None:
    """Анализ кешбэка за месяц"""
    year = ask_year()
    month = ask_month()
    try:
        result = analyze_cashback_categories(transactions, year, month)
    except Exception as e:
        print(f"Ошибка при анализе кешбэка: {e}")
        return

    print("\n=== Анализ кешбэка ===")
    if not result:
        print("Ничего не нашлось по заданной дате")
    else:
        print(result)


def transaction_search(transactions: List[Dict[str, Any]]) -> None:
    """Поиск по операциям"""
    try:
        query = get_search_query()
        result = search_transactions(transactions, query)
        print("\n=== Результаты поиска ===")
        print(result)
    except Exception as e:
        print(f"Ошибка при поиске транзакций: {e}")


def category_report(transactions: List[Dict[str, Any]]) -> None:
    """Отчёт по категории за 3 месяца"""
    try:
        df = pd.DataFrame(transactions)
        category = get_category_input()
        date = get_end_date()
        result = spending_by_category(df, category=category, date=date)
        print("\n=== Отчёт по категории ===")
        print(result)
    except Exception as e:
        print(f"Ошибка при формировании отчёта: {e}")


def main() -> None:
    print("Здравствуйте! Добро пожаловать в финансовый помощник")

    try:
        filepath = os.getenv("OPERATIONS_DIR")
        if filepath is None:
            print("Ошибка: переменная окружения OPERATIONS_DIR не установлена")
            return
        transactions = reader_from_excel(filepath)  # список словарей
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    while True:
        print("\n--- Главное меню ---")
        print("1. Сводная информация")
        print("2. Анализ кешбэка по категориям")
        print("3. Поиск транзакций")
        print("4. Отчёт по категории за последние 3 месяца")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            show_dashboard(transactions)
        elif choice == "2":
            cashback_analysis(transactions)
        elif choice == "3":
            transaction_search(transactions)
        elif choice == "4":
            category_report(transactions)
        elif choice == "0":
            print("До свидания")
            break
        else:
            print("Ошибка: неверный выбор. Введите 0–4.")


if __name__ == "__main__":
    main()
