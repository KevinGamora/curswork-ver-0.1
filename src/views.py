import datetime
import json
import os
from collections import defaultdict
from typing import Literal

import dotenv
import pandas as pd
import requests

from config import OP_DATA_DIR, USER_SETTINGS
from src.my_logger import Logger
from src.utils import get_json_from_dataframe

dotenv.load_dotenv()

logger = Logger("view").on_duty()


def event_response(date: str, optional_flag: Literal["M", "W", "Y", "ALL"] = "M") -> dict:
    """
    Главная функция.
    Собирает данные (траты, поступления, стоимости валют и акций) из других функций
    и возвращает готовый JSON ответ.

    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время (до введенной даты)
    :return: Готовый JSON ответ (словарь)
    """

    operation_date_data = operations_by_date_range(date, optional_flag)
    expenses, income = expenses_income(operation_date_data)

    currency_rates, stock_prices = get_currency_stocks(USER_SETTINGS)
    result = {"расходы": expenses, "доходы": income, "курсы_валют": currency_rates, "цены_акций": stock_prices}

    logger.info("Возвращенные данные указаны ниже")
    logger.info(result)

    return result


def operations_by_date_range(date: str, optional_flag: str = "M") -> list[dict]:
    """
    Функция для фильтрации данных об операциях по дате.
    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время (до введенной даты)
    :return: Список словарей с данными об операциях
    """

    # Задаем последнюю дату операций
    last_date = datetime.datetime.strptime(date, "%d.%m.%Y")

    # Задаем начальную дату операций. По умолчанию с начала месяца
    start_date = last_date.replace(day=1)

    if optional_flag == "W":
        # Берем данные с начала недели по день недели, соответствующий указанной дате
        days_between = last_date.day - last_date.weekday()
        start_date = last_date.replace(day=days_between)

    elif optional_flag == "Y":
        # Берем данные с начала года по день, соответствующий указанной дате
        start_date = last_date.replace(day=1, month=1)

    elif optional_flag == "ALL":
        # Берем все операции с начала до указанной даты
        start_date = last_date.replace(day=1, month=1, year=1)

    df = get_dataframe_from_file(OP_DATA_DIR)  # Считываем DataFrame из файла
    operation_data = get_json_from_dataframe(df)  # Считываем данные из DataFrame
    tmp = []  # Контейнер для операций, попадающих под требование

    # Отсекаем операции, которые не были выполнены или не покинули счет
    for operation in operation_data:
        if operation["Статус"] != "OK":
            continue

        operation_date = datetime.datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S")

        # Если дата операции подходит под требование - добавляем в контейнер
        if start_date < operation_date < last_date.replace(day=last_date.day + 1):
            tmp.append(operation)

    return tmp


def get_expense_categories(expense_categories: dict) -> dict:
    """
    Функция принимает на вход словарь с расходами по всем категориям, сортирует их по убыванию,
    оставляет только 7 категорий, где были наибольшие расходы. Все остальные категории
    помещает в категорию "Остальное".

    :param expense_categories: Словарь с расходами. {Категория(str): Расход(int)}.
    :return: Словарь. Данные о расходах, отсортированные по категориям.
    """

    total_amount = 0
    transfers_and_cash = []
    main_expenses = []

    for operation in dict(expense_categories).items():

        logger.info(operation)

        operation_category, operation_amount = operation
        total_amount += operation_amount

        if operation_category in ["Переводы", "Наличные"]:
            transfers_and_cash.append({"категория": operation_category, "сумма": round(operation_amount)})
        else:
            main_expenses.append({"категория": operation_category, "сумма": round(operation_amount)})

    # Сортируем данные по убыванию
    main_expenses.sort(key=lambda x: x["сумма"], reverse=True)
    transfers_and_cash.sort(key=lambda x: x["сумма"], reverse=True)

    # Если категорий расходов больше 7 - выбираем самые затратные. Остальным назначаем категорию "Остальное"
    if len(main_expenses) > 7:
        other_category_value = 0
        while len(main_expenses) > 7:
            popped_dict: dict = main_expenses.pop()
            other_category_value += popped_dict["сумма"]
        main_expenses.append({"категория": "Остальное", "сумма": other_category_value})

    return {"общая_сумма": total_amount, "основные": main_expenses, "переводы_и_наличные": transfers_and_cash}


def get_income_categories(income_categories: dict) -> dict:
    """
    Функция принимает на вход словарь с доходами по всем категориям и сортирует их по убыванию.

    :param income_categories: Словарь с доходами. {Категория(str): Доход(int)}.
    :return: Словарь. Данные о доходах, отсортированные по категориям.
    """

    total_amount = 0
    main_income = []

    for operation in dict(income_categories).items():
        logger.debug(operation)
        operation_category, operation_amount = operation
        total_amount += operation_amount

        main_income.append({"категория": operation_category, "сумма": round(operation_amount)})

    main_income.sort(key=lambda x: x["сумма"], reverse=True)

    return {"общая_сумма": total_amount, "основные": main_income}


def expenses_income(operations: list[dict]) -> tuple[dict, dict]:
    """
    Функция принимает на вход список словарей с данными об операциях, отсортированных по дате.

    :param operations: Список словарей
    :return: Словари (расходы, доходы)
    """

    income_categories: defaultdict = defaultdict(int)
    expense_categories: defaultdict = defaultdict(int)

    for operation in operations:
        operation_amount = operation["Сумма платежа"]
        operation_category = operation["Категория"]

        if operation_amount < 0:
            expense_categories[operation_category] += abs(operation_amount)
        else:
            income_categories[operation_category] += abs(operation_amount)

    expenses = get_expense_categories(expense_categories)
    income = get_income_categories(income_categories)

    return expenses, income


def get_currency_stocks(file_path: str = USER_SETTINGS) -> tuple[list, list]:
    """
    Функция для определения курса валюты и цены акций, указанных в настройках файла.
    :param file_path: Путь до файла с настройками пользователя
    :return: Списки. (курсы валюты, акции)
    """

    with open(file_path, "r", encoding="utf8") as user_file:
        user_settings = json.load(user_file)
        user_currencies = user_settings["валюты_пользователя"]
        user_stocks = user_settings["акции_пользователя"]

    currency_list = []
    stock_list = []

    for currency in user_currencies:
        currency_price = get_currency_price(currency)
        currency_list.append({"валюта": currency, "курс": currency_price})

    for stock in user_stocks:
        stock_price = get_stock_price(stock)
        stock_list.append({"акция": stock, "цена": stock_price})

    return currency_list, stock_list


def get_currency_price(currency: str, to: str = "RUB") -> None | float:
    """
    Функция для выполнения запроса API для получения цены валюты в рублевом эквиваленте.
    Сервис API "Exchange Rates Data API" https://apilayer.com/marketplace/exchangerates_data-api

    :param currency: Основная валюта
    :param to: В какую валюту необходимо конвертировать
    :return: Если нет ответа - None, в противном случае float
    """

    api_key = os.getenv("CUR_API")
    url = "https://api.apilayer.com/exchangerates_data/convert?"

    params: dict[str, str | int] = {"to": to, "from": currency, "amount": 1}

    response = requests.get(url, params=params, headers={"apikey": api_key})
    if response.status_code != 200:
        return None

    result: float | None = response.json().get("result")
    return result


def get_stock_price(stock: str) -> None | float:
    """
    Функция для получения цены акции в долларах по коду акции.
    Сервис: https://finnhub.io/docs/api/quote

    :param stock: Код акции
    :return:
    """

    url = "https://api.finnhub.io/api/v1/quote?"
    params = {"symbol": stock, "token": os.getenv("FINNHUB_API")}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    result: float | None = response.json().get("c")

    return result


def get_dataframe_from_file(file_path: str) -> pd.DataFrame:
    """
    Функция принимает путь до файла и возвращает DataFrame, считывая его из файла.
    :param file_path:
    :return:
    """
    return pd.read_excel(file_path)
