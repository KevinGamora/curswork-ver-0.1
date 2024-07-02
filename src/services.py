import re

from config import OP_DATA_DIR
from src.my_logger import Logger
from src.utils import read_file_data

logger = Logger("services").on_duty()

def simple_search(search_field: str, file_path: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция для поиска операций по полю поиска в описании операции или в категории.
    :param search_field: Строка для поиска.
    :param file_path: Путь до файла
    :return: Список подходящих по поиску операций.
    """

    search_field = search_field.lower()
    all_data_op = read_file_data(file_path)

    tmp = []
    for op in all_data_op:
        category_op = op["Категория"] or " "
        description_op = op["Описание"] or " "

        if search_field in category_op.lower() or search_field in description_op.lower():
            tmp.append(op)

    logger.debug(f"В поиск передано: {search_field}. Найдено совпадений: {len(tmp)}")

    return tmp

def search_by_persons(file_path: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция возвращает список операций физическим лицам
    :param file_path: путь до excel файла
    :return: Список операций
    """

    tmp = []
    data_op = read_file_data(file_path)

    for op in data_op:
        if op["Категория"] != "Переводы":
            continue

        regex = r"\w* [\w]{1}\."
        result = re.findall(regex, op["Описание"])
        if result:
            tmp.append(op)

    logger.debug(f"Найдено совпадений: {len(tmp)}")

    return tmp
