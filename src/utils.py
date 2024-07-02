import numpy as np
import pandas as pd

def read_data_from_file(file_path: str) -> list[dict]:
    """
    Функция читает данные из файла Excel и возвращает их в виде списка словарей.
    :param file_path: Путь к файлу с данными
    :return: Список словарей, представляющих данные
    """

    data = pd.read_excel(file_path).replace({np.nan: None})
    data_as_dict = data.to_dict("records")

    return data_as_dict

def get_json_from_dataframe(df: pd.DataFrame) -> list[dict]:
    """
    Функция конвертирует DataFrame в список словарей.
    :param df: DataFrame для конвертации
    :return: Список словарей, содержащих данные из DataFrame
    """
    return df.replace({np.nan: None}).to_dict("records")
