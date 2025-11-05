import unittest
from typing import Any, Dict, List
from unittest.mock import Mock, patch

from src.main import cashback_analysis, main, show_dashboard


class TestMainModule(unittest.TestCase):

    def setUp(self) -> None:
        """Настройка перед каждым тестом."""
        self.sample_transactions: List[Dict[str, Any]] = [
            {
                "Дата операции": "01.01.2024 12:00:00",
                "Номер карты": "1234567890123456",
                "Сумма платежа": -1000.0,
                "Категория": "Супермаркеты",
                "Описание": "Пятёрочка",
                "Статус": "OK",
            },
            {
                "Дата операции": "05.01.2024 18:00:00",
                "Номер карты": "9876543210987654",
                "Сумма платежа": -500.0,
                "Категория": "Топливо",
                "Описание": "АЗС",
                "Статус": "OK",
            },
        ]

    @patch("src.main.reader_from_excel")
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["5", "0"])  # Неверный выбор, затем выход
    def test_main_invalid_choice_then_exit(self, mock_input: Mock, mock_print: Mock, mock_reader: Mock) -> None:
        """Тест обработки неверного выбора в меню."""
        mock_reader.return_value = self.sample_transactions

        with patch("src.main.os.getenv", return_value="test_path.xlsx"):
            main()

        # Проверяем сообщение об ошибке
        mock_print.assert_any_call("Ошибка: неверный выбор. Введите 0–4.")

    @patch("src.main.main_views")
    @patch("src.main.get_date_input")
    @patch("builtins.print")
    def test_show_dashboard_success(self, mock_print: Mock, mock_get_date: Mock, mock_main_views: Mock) -> None:
        """Тест успешного отображения dashboard."""
        mock_get_date.return_value = "2024-01-01 12:00:00"
        mock_main_views.return_value = "Dashboard content"

        show_dashboard(self.sample_transactions)

        mock_print.assert_any_call("\n=== Главная страница ===")
        mock_print.assert_any_call("Dashboard content")

    @patch("src.main.main_views", side_effect=Exception("View error"))
    @patch("src.main.get_date_input")
    @patch("builtins.print")
    def test_show_dashboard_error(self, mock_print: Mock, mock_get_date: Mock, mock_main_views: Mock) -> None:
        """Тест обработки ошибки в dashboard."""
        mock_get_date.return_value = "2024-01-01 12:00:00"

        show_dashboard(self.sample_transactions)

        mock_print.assert_any_call("Ошибка при формировании главной страницы: View error")

    @patch("src.main.analyze_cashback_categories")
    @patch("src.main.ask_year")
    @patch("src.main.ask_month")
    @patch("builtins.print")
    def test_cashback_analysis_success(
        self, mock_print: Mock, mock_ask_month: Mock, mock_ask_year: Mock, mock_analyze: Mock
    ) -> None:
        """Тест успешного анализа кешбэка."""
        mock_ask_year.return_value = 2024
        mock_ask_month.return_value = 1
        mock_analyze.return_value = [{"category": "Food", "cashback": 100}]

        cashback_analysis(self.sample_transactions)

        mock_print.assert_any_call("\n=== Анализ кешбэка ===")
        mock_print.assert_any_call([{"category": "Food", "cashback": 100}])


if __name__ == "__main__":
    unittest.main()
