import numpy as np
import pandas as pd


def read_file_data(file_path: str) -> list[dict]:
    """
    Функция для чтения excel файла и возвращения данных в виде списка словарей
    :param file_path: Путь до файла с данными
    :return: Данные в виде списка словарей
    """

    data = pd.read_excel(file_path).replace({np.nan: None})
    data_as_dict = data.to_dict("records")

    return data_as_dict


def get_json_from_dataframe(df: pd.DataFrame) -> list[dict]:
    """
    Функция возвращает список словарей чтением DataFrame
    :param df:
    :return:
    """
    return df.replace({np.nan: None}).to_dict("records")
