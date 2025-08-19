import pandas as pd
from datetime import datetime

from src.config import DATA_DIR
from src.utils import reader_from_excel
from src.views import main_views
from src.services import analyze_cashback_categories, search_transactions
from src.reports import spending_by_category


def show_dashboard(transactions):
    """Главная страница: приветствие, карты, топ-5 трат, валюты, акции"""
    while True:
        try:
            time_user = input("Введите дату (YYYY-MM-DD HH:MM:SS) или Enter для текущей: ").strip()
            if not time_user:
                time_user = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datetime.strptime(time_user, "%Y-%m-%d %H:%M:%S")  # проверка формата
            result = main_views(time_user)
            print("\n=== Главная страница ===")
            print(result)
            break
        except ValueError:
            print("Ошибка: неверный формат даты. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка при формировании главной страницы: {e}")
            break


def cashback_analysis(transactions):
    """Анализ кешбэка за месяц"""
    while True:
        try:
            while True:
                year_input = input("Введите год (например, 2025): ").strip()
                if not year_input.isdigit():
                    print("Ошибка: нужно ввести число для года.")
                    continue
                year = int(year_input)
                if year < 1900 or year > 2026:
                    print("Ошибка: введите реальный год (1900–2026).")
                    continue
                break

            # ввод месяца
            while True:
                month_input = input("Введите месяц (1-12): ").strip()
                if not month_input.isdigit():
                    print("Ошибка: нужно ввести число для месяца.")
                    continue
                month = int(month_input)
                if not (1 <= month <= 12):
                    print("Месяц должен быть от 1 до 12.")
                    continue
                break

            result = analyze_cashback_categories(transactions, year, month)
            print("\n=== Анализ кешбэка ===")
            if not result:
                print("Ничего не нашлось по заданной дате")
            else:
                print(result)
            break
        except Exception as e:
            print(f"Ошибка при анализе кешбэка: {e}")
            break


def transaction_search(transactions):
    """Поиск по операциям"""
    try:
        query = input("Введите слово или фразу для поиска: ").strip()
        if not query:
            print("Ошибка: строка поиска не может быть пустой.")
            return
        result = search_transactions(transactions, query)
        print("\n=== Результаты поиска ===")
        print(result)
    except Exception as e:
        print(f"Ошибка при поиске транзакций: {e}")


def category_report(transactions):
    """Отчёт по категории за 3 месяца"""
    try:
        df = pd.DataFrame(transactions)
        category = input("Введите категорию (например, Продукты): ").strip()
        if not category:
            print("Ошибка: категория не может быть пустой.")
            return
        date = input("Введите конечную дату (ДД.ММ.ГГГГ) или Enter для текущей: ").strip()
        if date:
            try:
                datetime.strptime(date, "%d.%m.%Y")  # проверка формата
            except ValueError:
                print("Ошибка: неверный формат даты, используем текущую.")
                date = None
        else:
            date = None

        result = spending_by_category(df, category=category, date=date)
        print("\n=== Отчёт по категории ===")
        print(result)
    except Exception as e:
        print(f"Ошибка при формировании отчёта: {e}")


def main():
    print("Здравствуйте! Добро пожаловать в финансовый помощник")

    try:
        filepath = DATA_DIR / "operations.xlsx"
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
