import numpy as np
import pandas as pd


def чтение_данных_из_файла(путь_файла: str) -> list[dict]:
    """
    Функция читает данные из файла Excel и возвращает их в виде списка словарей.
    :param путь_файла: Путь к файлу с данными
    :return: Список словарей, представляющих данные
    """

    данные = pd.read_excel(путь_файла).replace({np.nan: None})
    данные_как_словарь = данные.to_dict("records")

    return данные_как_словарь


def получить_json_из_dataframe(df: pd.DataFrame) -> list[dict]:
    """
    Функция конвертирует DataFrame в список словарей.
    :param df: DataFrame для конвертации
    :return: Список словарей, содержащих данные из DataFrame
    """
    return df.replace({np.nan: None}).to_dict("records")
