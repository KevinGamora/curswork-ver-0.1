from pandas import Timestamp
from src.reports import spending_by_category

def test_spending_by_category(dataframe_dat_cat):
    """
    Тестирование функции spending_by_category для фильтрации данных по категории трат и дате.
    :param dataframe_dat_cat: Тестовый DataFrame с данными о транзакциях.
    """

    # Проверка для указанной даты "1.02.2000"
    expected_result_date_specified = [
        {"Дата операции": Timestamp("2000-01-01 00:00:00"), "Категория": "Топливо"},
        {"Дата операции": Timestamp("2000-01-04 00:00:00"), "Категория": "Топливо"},
    ]
    assert spending_by_category(dataframe_dat_cat, "Топливо", "1.02.2000").to_dict("records") == expected_result_date_specified

    # Проверка для текущей даты (без указания даты)
    expected_result_no_date_specified = []
    assert spending_by_category(dataframe_dat_cat, "Топливо").to_dict("records") == expected_result_no_date_specified
