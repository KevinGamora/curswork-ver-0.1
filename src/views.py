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


def post_events_response(date: str, optional_flag: Literal["M", "W", "Y", "ALL"] = "M") -> dict:
    """
    Главная функция.
    Собирает данные(траты, поступления, стоимости валют и акций) из других функций
    и возвращает готовый JSON ответ

    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время(до введенной даты)
    :return: готовый JSON ответ (словарь)
    """

    f_by_date_operations = get_operations_by_date_range(date, optional_flag)
    expences, income = get_expences_income(f_by_date_operations)

    currency_rates, stocks_prices = get_currency_stocks(USER_SETTINGS)
    result = {"expences": expences, "income": income, "currency_rates": currency_rates, "stock_prices": stocks_prices}

    logger.info("Возвращенные данные указаны ниже")
    logger.info(result)

    return result


def get_operations_by_date_range(date: str, optional_flag: str = "M") -> list[dict]:
    """
    Функция для фильтрации данных об операциях по дате.
    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время(до введенной даты)
    :return: Список словарей с данными об операциях
    """

    # Задаём последнюю дату операций
    last_date = datetime.datetime.strptime(date, "%d.%m.%Y")

    # Задаём стартовую дату операций. По умолчанию с начала месяца
    start_date = last_date.replace(day=1)

    if optional_flag == "W":
        # Берем данные с начала недели по день недели соответствующий указаной дате
        days_between = last_date.day - last_date.weekday()
        start_date = last_date.replace(day=days_between)

    elif optional_flag == "Y":
        # Берем данные с начала года по день соответствующий указаной дате
        start_date = last_date.replace(day=1, month=1)

    elif optional_flag == "ALL":
        # Берем все операции с начала до указанной даты
        start_date = last_date.replace(day=1, month=1, year=1)

    df = get_dataframe_from_file(OP_DATA_DIR)  # Считываем DataFrame из файла
    op_data = get_json_from_dataframe(df)  # Считываем данные из DataFrame
    tmp = []  # Контейнер для операций попадающих под требование

    # Отсекаем операции которые не были совершены и деньги не покинули счёт
    for op in op_data:
        if op["Статус"] != "OK":
            continue

        op_date = datetime.datetime.strptime(op["Дата операции"], "%d.%m.%Y %H:%M:%S")

        # Если дата операции подходит под требование - добавляем в контейнер
        if start_date < op_date < last_date.replace(day=last_date.day + 1):
            tmp.append(op)

    return tmp


def get_expences_categories(expences_categories: dict) -> dict:
    """
    Функция принимает на вход словарь с тратами по всем категориям, сортирует по убыванию,
    оставляет только 7 категорий, где были самые значительные траты. Все остальные траты
    помещает в категорию "Остальное".

    :param expences_categories: Словарь с тратами. {Категория(str): Трата(int)}.
    :return: Словарь. Данные о тратах отсортированные по категориям.
    """

    total_amount = 0
    transfers_and_cash = []
    expences_main = []

    for op in dict(expences_categories).items():

        logger.info(op)

        op_category, op_amount = op
        total_amount += op_amount

        if op_category in ["Переводы", "Наличные"]:
            transfers_and_cash.append({"category": op_category, "amount": round(op_amount)})
        else:
            expences_main.append({"category": op_category, "amount": round(op_amount)})

    # Сортируем данные по убыванию
    expences_main.sort(key=lambda x: x["amount"], reverse=True)
    transfers_and_cash.sort(key=lambda x: x["amount"], reverse=True)

    # Если категорий трат больше 7 - выделяем самые затратные. Остальным назначаем категорию "Остальное"
    if len(expences_main) > 7:
        other_cat_value = 0
        while len(expences_main) > 7:
            popped_dict: dict = expences_main.pop()
            other_cat_value += popped_dict["amount"]
        expences_main.append({"category": "Остальное", "amount": other_cat_value})

    return {"total_amount": total_amount, "main": expences_main, "transfers_and_cash": transfers_and_cash}


def get_income_categories(income_categories: dict) -> dict:
    """
    Функция принимает на вход словарь с поступлениями по всем категориям, сортирует по убыванию.

    :param income_categories: Словарь с поступлениями. {Категория(str): Поступление(int)}.
    :return: Словарь. Данные о поступлениях отсортированные по категориям.
    """

    total_amount = 0
    income_main = []

    for op in dict(income_categories).items():
        logger.debug(op)
        op_category, op_amount = op
        total_amount += op_amount

        income_main.append({"category": op_category, "amount": round(op_amount)})

    income_main.sort(key=lambda x: x["amount"], reverse=True)

    return {"total_amount": total_amount, "main": income_main}


def get_expences_income(operations: list[dict]) -> tuple[dict, dict]:
    """
    Функция принимает на вход список словарей с данными о всех отсортированных по дате операциях.

    :param operations: Список словарей
    :return: Словари (траты, поступления)
    """

    income_categories: defaultdict = defaultdict(int)
    expences_categories: defaultdict = defaultdict(int)

    for op in operations:
        op_sum = op["Сумма платежа"]
        op_category = op["Категория"]

        if op_sum < 0:
            expences_categories[op_category] += abs(op_sum)
        else:
            income_categories[op_category] += abs(op_sum)

    expences = get_expences_categories(expences_categories)
    incomes = get_income_categories(income_categories)

    return expences, incomes


def get_currency_stocks(file_path: str = USER_SETTINGS) -> tuple[list, list]:
    """
    Функция для определения курса валюты и цены акций, указанных в file_path настройках.
    :param file_path: Путь до файла с настройками пользователя
    :return: Списки. (курсы валюты, акции)
    """

    with open(file_path, "r", encoding="utf8") as user_file:
        user_settings = json.load(user_file)
        user_currencies = user_settings["user_currencies"]
        user_stocks = user_settings["user_stocks"]

    currency_list = []
    stocks_list = []

    for cur in user_currencies:
        cur_price = get_currency_price(cur)
        currency_list.append({"currency": cur, "rate": cur_price})

    for stock in user_stocks:
        stock_price = get_stock_price(stock)
        stocks_list.append({"stock": stock, "price": stock_price})

    return currency_list, stocks_list


def get_currency_price(currency: str, into: str = "RUB") -> None | float:
    """
    Функция для обращения по API запросу для получения цены валюты в рублёвом еквиваленте
    API-сервис "Exchange Rates Data API" https://apilayer.com/marketplace/exchangerates_data-api

    :param currency: Основная валюта
    :param into: В какую валюту необходимо конвертировать
    :return: Если ответа нет - None, в успешном случае float
    """

    api_key = os.getenv("CUR_API")
    url = "https://api.apilayer.com/exchangerates_data/convert?"

    params: dict[str, str | int] = {"to": into, "from": currency, "amount": 1}

    response = requests.get(url, params=params, headers={"apikey": api_key})
    if response.status_code != 200:
        return None

    result: float | None = response.json().get("result")
    return result


def get_stock_price(stock: str) -> None | float:
    """
    Функция получает цену акции в долларах по коду.
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
    Функция принимает путь до файла и возвращает Dataframe чтением файла
    :param file_path:
    :return:
    """
    return pd.read_excel(file_path)
