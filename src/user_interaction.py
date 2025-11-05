from datetime import datetime


def ask_year() -> int:
    while True:
        year_input = input("Введите год (например, 2025): ").strip()
        if not year_input.isdigit():
            print("Ошибка: нужно ввести число для года.")
            continue
        year = int(year_input)
        if year < 1900 or year > 2026:
            print("Ошибка: введите реальный год (1900–2026).")
            continue
        return year


def ask_month() -> int:
    while True:
        month_input = input("Введите месяц (1-12): ").strip()
        if not month_input.isdigit():
            print("Ошибка: нужно ввести число для месяца.")
            continue
        month = int(month_input)
        if not (1 <= month <= 12):
            print("Месяц должен быть от 1 до 12.")
            continue
        return month


def get_date_input(prompt: str, default_current: bool = True) -> str:
    """Получение даты от пользователя с проверкой формата"""
    while True:
        try:
            time_user = input(prompt).strip()
            if not time_user and default_current:
                time_user = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datetime.strptime(time_user, "%Y-%m-%d %H:%M:%S")
            return time_user
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS")


def get_end_date() -> str | None:
    """Получение конечной даты для отчёта"""
    while True:
        date = input("Введите конечную дату (ДД.ММ.ГГГГ) или Enter для текущей: ").strip()
        if not date:
            return None
        try:
            datetime.strptime(date, "%d.%m.%Y")
            return date
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте ДД.ММ.ГГГГ")


def get_category_input() -> str:
    """Получение категории от пользователя"""
    while True:
        category = input("Введите категорию (например, Продукты): ").strip()
        if category:
            return category
        print("Ошибка: категория не может быть пустой.")


def get_search_query() -> str:
    """Получение поискового запроса"""
    while True:
        query = input("Введите слово или фразу для поиска: ").strip()
        if query:
            return query
        print("Ошибка: строка поиска не может быть пустой.")
