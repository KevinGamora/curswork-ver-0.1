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


def ответ_по_событиям(date: str, optional_flag: Literal["M", "W", "Y", "ALL"] = "M") -> dict:
    """
    Главная функция.
    Собирает данные (траты, поступления, стоимости валют и акций) из других функций
    и возвращает готовый JSON ответ.

    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время (до введенной даты)
    :return: Готовый JSON ответ (словарь)
    """

    данные_по_дате_операций = операции_по_диапазону_дат(date, optional_flag)
    расходы, доходы = расходы_доходы(данные_по_дате_операций)

    курсы_валют, цены_акций = получить_валюты_акции(USER_SETTINGS)
    результат = {"расходы": расходы, "доходы": доходы, "курсы_валют": курсы_валют, "цены_акций": цены_акций}

    logger.info("Возвращенные данные указаны ниже")
    logger.info(результат)

    return результат


def операции_по_диапазону_дат(date: str, optional_flag: str = "M") -> list[dict]:
    """
    Функция для фильтрации данных об операциях по дате.
    :param date: Формат даты День.Месяц.Год
    :param optional_flag: Отображение операций за месяц/неделю/год/всё время (до введенной даты)
    :return: Список словарей с данными об операциях
    """

    # Задаем последнюю дату операций
    последняя_дата = datetime.datetime.strptime(date, "%d.%m.%Y")

    # Задаем начальную дату операций. По умолчанию с начала месяца
    начальная_дата = последняя_дата.replace(day=1)

    if optional_flag == "W":
        # Берем данные с начала недели по день недели, соответствующий указанной дате
        дни_между = последняя_дата.day - последняя_дата.weekday()
        начальная_дата = последняя_дата.replace(day=дни_между)

    elif optional_flag == "Y":
        # Берем данные с начала года по день, соответствующий указанной дате
        начальная_дата = последняя_дата.replace(day=1, month=1)

    elif optional_flag == "ALL":
        # Берем все операции с начала до указанной даты
        начальная_дата = последняя_дата.replace(day=1, month=1, year=1)

    df = получить_dataframe_из_файла(OP_DATA_DIR)  # Считываем DataFrame из файла
    данные_операций = get_json_from_dataframe(df)  # Считываем данные из DataFrame
    tmp = []  # Контейнер для операций, попадающих под требование

    # Отсекаем операции, которые не были выполнены или не покинули счет
    for операция in данные_операций:
        if операция["Статус"] != "OK":
            continue

        дата_операции = datetime.datetime.strptime(операция["Дата операции"], "%d.%m.%Y %H:%M:%S")

        # Если дата операции подходит под требование - добавляем в контейнер
        if начальная_дата < дата_операции < последняя_дата.replace(day=последняя_дата.day + 1):
            tmp.append(операция)

    return tmp


def получить_категории_расходов(категории_расходов: dict) -> dict:
    """
    Функция принимает на вход словарь с расходами по всем категориям, сортирует их по убыванию,
    оставляет только 7 категорий, где были наибольшие расходы. Все остальные категории
    помещает в категорию "Остальное".

    :param категории_расходов: Словарь с расходами. {Категория(str): Расход(int)}.
    :return: Словарь. Данные о расходах, отсортированные по категориям.
    """

    общая_сумма = 0
    переводы_и_наличные = []
    основные_расходы = []

    for операция in dict(категории_расходов).items():

        logger.info(операция)

        категория_операции, сумма_операции = операция
        общая_сумма += сумма_операции

        if категория_операции in ["Переводы", "Наличные"]:
            переводы_и_наличные.append({"категория": категория_операции, "сумма": round(сумма_операции)})
        else:
            основные_расходы.append({"категория": категория_операции, "сумма": round(сумма_операции)})

    # Сортируем данные по убыванию
    основные_расходы.sort(key=lambda x: x["сумма"], reverse=True)
    переводы_и_наличные.sort(key=lambda x: x["сумма"], reverse=True)

    # Если категорий расходов больше 7 - выбираем самые затратные. Остальным назначаем категорию "Остальное"
    if len(основные_расходы) > 7:
        другая_категория_значение = 0
        while len(основные_расходы) > 7:
            popped_dict: dict = основные_расходы.pop()
            другая_категория_значение += popped_dict["сумма"]
        основные_расходы.append({"категория": "Остальное", "сумма": другая_категория_значение})

    return {"общая_сумма": общая_сумма, "основные": основные_расходы, "переводы_и_наличные": переводы_и_наличные}


def получить_категории_доходов(категории_доходов: dict) -> dict:
    """
    Функция принимает на вход словарь с доходами по всем категориям и сортирует их по убыванию.

    :param категории_доходов: Словарь с доходами. {Категория(str): Доход(int)}.
    :return: Словарь. Данные о доходах, отсортированные по категориям.
    """

    общая_сумма = 0
    основные_доходы = []

    for операция in dict(категории_доходов).items():
        logger.debug(операция)
        категория_операции, сумма_операции = операция
        общая_сумма += сумма_операции

        основные_доходы.append({"категория": категория_операции, "сумма": round(сумма_операции)})

    основные_доходы.sort(key=lambda x: x["сумма"], reverse=True)

    return {"общая_сумма": общая_сумма, "основные": основные_доходы}


def расходы_доходы(операции: list[dict]) -> tuple[dict, dict]:
    """
    Функция принимает на вход список словарей с данными об операциях, отсортированных по дате.

    :param операции: Список словарей
    :return: Словари (расходы, доходы)
    """

    категории_доходов: defaultdict = defaultdict(int)
    категории_расходов: defaultdict = defaultdict(int)

    for операция in операции:
        сумма_операции = операция["Сумма платежа"]
        категория_операции = операция["Категория"]

        if сумма_операции < 0:
            категории_расходов[категория_операции] += abs(сумма_операции)
        else:
            категории_доходов[категория_операции] += abs(сумма_операции)

    расходы = получить_категории_расходов(категории_расходов)
    доходы = получить_категории_доходов(категории_доходов)

    return расходы, доходы


def получить_валюты_акции(file_path: str = USER_SETTINGS) -> tuple[list, list]:
    """
    Функция для определения курса валюты и цены акций, указанных в настройках файла.
    :param file_path: Путь до файла с настройками пользователя
    :return: Списки. (курсы валюты, акции)
    """

    with open(file_path, "r", encoding="utf8") as user_file:
        настройки_пользователя = json.load(user_file)
        валюты_пользователя = настройки_пользователя["валюты_пользователя"]
        акции_пользователя = настройки_пользователя["акции_пользователя"]

    список_валют = []
    список_акций = []

    for валюта in валюты_пользователя:
        цена_валюты = получить_цену_валюты(валюта)
        список_валют.append({"валюта": валюта, "курс": цена_валюты})

    for акция in акции_пользователя:
        цена_акции = получить_цену_акции(акция)
        список_акций.append({"акция": акция, "цена": цена_акции})

    return список_валют, список_акций


def получить_цену_валюты(валюта: str, в: str = "RUB") -> None | float:
    """
    Функция для выполнения запроса API для получения цены валюты в рублевом эквиваленте.
    Сервис API "Exchange Rates Data API" https://apilayer.com/marketplace/exchangerates_data-api

    :param валюта: Основная валюта
    :param в: В какую валюту необходимо конвертировать
    :return: Если нет ответа - None, в противном случае float
    """

    ключ_api = os.getenv("CUR_API")
    url = "https://api.apilayer.com/exchangerates_data/convert?"

    параметры: dict[str, str | int] = {"to": в, "from": валюта, "amount": 1}

    ответ = requests.get(url, params=параметры, headers={"apikey": ключ_api})
    if ответ.status_code != 200:
        return None

    результат: float | None = ответ.json().get("result")
    return результат


def получить_цену_акции(акция: str) -> None | float:
    """
    Функция для получения цены акции в долларах по коду акции.
    Сервис: https://finnhub.io/docs/api/quote

    :param акция: Код акции
    :return:
    """

    url = "https://api.finnhub.io/api/v1/quote?"
    параметры = {"symbol": акция, "token": os.getenv("FINNHUB_API")}

    ответ = requests.get(url, params=параметры)

    if ответ.status_code != 200:
        return None

    результат: float | None = ответ.json().get("c")

    return результат


def получить_dataframe_из_файла(file_path: str) -> pd.DataFrame:
    """
    Функция принимает путь до файла и возвращает DataFrame, считывая его из файла.
    :param file_path:
    :return:
    """
    return pd.read_excel(file_path)
