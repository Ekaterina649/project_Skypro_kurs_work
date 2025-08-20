import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from src.user_interaction import (ask_month, ask_year, get_category_input, get_date_input, get_end_date,
                                  get_search_query)


class TestUserInteraction(unittest.TestCase):

    # Тестирование ask_year
    @patch("builtins.input")
    @patch("builtins.print")
    def test_ask_year_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["2024"]
        result = ask_year()
        self.assertEqual(result, 2024)
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_ask_year_invalid_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["abc", "1899", "2027", "2024"]
        result = ask_year()
        self.assertEqual(result, 2024)
        self.assertEqual(mock_print.call_count, 3)

    # Тестирование ask_month
    @patch("builtins.input")
    @patch("builtins.print")
    def test_ask_month_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["6"]
        result = ask_month()
        self.assertEqual(result, 6)
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_ask_month_invalid_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["abc", "0", "13", "5"]
        result = ask_month()
        self.assertEqual(result, 5)
        self.assertEqual(mock_print.call_count, 3)

    # Тестирование get_date_input
    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_date_input_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["2024-12-31 23:59:59"]
        result = get_date_input("Введите дату: ")
        self.assertEqual(result, "2024-12-31 23:59:59")
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_date_input_empty_default_current(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = [""]
        result = get_date_input("Введите дату: ")
        # Проверяем, что возвращается строка в правильном формате
        datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_date_input_invalid_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["invalid", "2024-12-31 23:59:59"]
        result = get_date_input("Введите дату: ")
        self.assertEqual(result, "2024-12-31 23:59:59")
        mock_print.assert_called_once()

    # Тестирование get_end_date
    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_end_date_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["31.12.2024"]
        result = get_end_date()
        self.assertEqual(result, "31.12.2024")
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_end_date_empty(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = [""]
        result = get_end_date()
        self.assertIsNone(result)
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_end_date_invalid_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["invalid", "31.12.2024"]
        result = get_end_date()
        self.assertEqual(result, "31.12.2024")
        mock_print.assert_called_once()

    # Тестирование get_category_input
    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_category_input_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["Продукты"]
        result = get_category_input()
        self.assertEqual(result, "Продукты")
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_category_input_empty_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["", " ", "Продукты"]
        result = get_category_input()
        self.assertEqual(result, "Продукты")
        self.assertEqual(mock_print.call_count, 2)

    # Тестирование get_search_query
    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_search_query_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["магазин"]
        result = get_search_query()
        self.assertEqual(result, "магазин")
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_search_query_empty_then_valid(self, mock_print: Mock, mock_input: Mock) -> None:
        mock_input.side_effect = ["", " ", "магазин"]
        result = get_search_query()
        self.assertEqual(result, "магазин")
        self.assertEqual(mock_print.call_count, 2)


if __name__ == "__main__":
    unittest.main()
