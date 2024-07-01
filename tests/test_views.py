import unittest
from unittest.mock import patch

from src.views import (
    get_currency_stocks,
    get_expences_categories,
    get_expences_income,
    get_income_categories,
    get_operations_by_date_range,
    post_events_response,
)


class TestPostEventsResponse(unittest.TestCase):
    @patch("requests.get")
    def test_post_events_response(self, get_mock):
        get_mock.return_value.status_code = 200
        get_mock.return_value.json.return_value = {"result": 99.42, "c": 99.42}

        result = post_events_response("01.10.2018", "W")
        self.assertEqual(result, post_events_response_result)

        get_mock.return_value.status_code = 400
        result_none = post_events_response("01.10.2018", "W")
        self.assertEqual(result_none, post_events_response_result_none)


class TestGetIncomeCategories(unittest.TestCase):
    def test_get_income_categories(self):
        incomes = {"Зарплата": 1000, "Подарок": 2000}
        expected_result = {
            "total_amount": 3000,
            "main": [{"category": "Подарок", "amount": 2000}, {"category": "Зарплата", "amount": 1000}],
        }

        result = get_income_categories(incomes)
        self.assertEqual(result, expected_result)


class TestGetExpencesIncome(unittest.TestCase):
    def test_get_expences_income(self):
        operations = operations_m
        expected_result = expenses_income_results

        result = get_expences_income(operations)
        self.assertEqual(result, expected_result)

        single_operation = [{"Сумма платежа": 100, "Категория": "Пополнение"}]
        expected_result_single = (
            {"total_amount": 0, "main": [], "transfers_and_cash": []},
            {"total_amount": 100, "main": [{"category": "Пополнение", "amount": 100}]},
        )

        result_single = get_expences_income(single_operation)
        self.assertEqual(result_single, expected_result_single)


class TestGetCurrencyStocks(unittest.TestCase):
    @patch("requests.get")
    def test_get_currency_stocks(self, get_mock):
        get_mock.return_value.status_code = 200
        get_mock.return_value.json.return_value = {"result": 99.42, "c": 99.42}

        result = get_currency_stocks()
        self.assertEqual(result, cur_stocks_result)


class TestGetExpencesCategories(unittest.TestCase):
    def test_get_expences_categories(self):
        expences = {
            "Топливо": 1000,
            "Супермаркет": 2000,
            "Наличные": 3000,
            "Красота": 4000,
            "Развлечение": 5000,
            "Одежда": 6000,
            "Фастфуд": 7000,
            "Благотворительность": 8000,
            "Ремонт": 9000,
        }

        expected_result = {
            "total_amount": 45000,
            "main": [
                {"category": "Ремонт", "amount": 9000},
                {"category": "Благотворительность", "amount": 8000},
                {"category": "Фастфуд", "amount": 7000},
                {"category": "Одежда", "amount": 6000},
                {"category": "Развлечение", "amount": 5000},
                {"category": "Красота", "amount": 4000},
                {"category": "Супермаркет", "amount": 2000},
                {"category": "Остальное", "amount": 1000},
            ],
            "transfers_and_cash": [{"category": "Наличные", "amount": 3000}],
        }

        result = get_expences_categories(expences)
        self.assertEqual(result, expected_result)


class TestGetOperationsByDateRange(unittest.TestCase):
    def test_get_operations_by_date_range(self):
        result_m = get_operations_by_date_range("01.10.2018")
        self.assertEqual(result_m, operations_m)

        result_w = get_operations_by_date_range("01.10.2018", "W")
        self.assertEqual(result_w, operations_w)

        result_all = get_operations_by_date_range("01.02.2018", "ALL")
        self.assertEqual(result_all, operations_all)

        result_year = get_operations_by_date_range("01.02.2018", "Y")
        self.assertEqual(result_year, operations_all)


if __name__ == "__main__":
    unittest.main()

