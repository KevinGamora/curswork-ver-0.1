import re

from config import OP_DATA_DIR
from src.my_logger import Logger
from src.utils import read_file_data

logger = Logger("services").on_duty()


def simple_searching(search_field: str, file_path: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция для поиска операций по полю поиска в описании операции или в категории.
    :param search_field: Строка для поиска.
    :param file_path: Путь до файла
    :return: Список подходящих по поиску операций.
    """

    search_field = search_field.lower()
    all_op_data = read_file_data(file_path)

    tmp = []
    for op in all_op_data:
        op_category = op["Категория"] or " "
        op_descr = op["Описание"] or " "

        if search_field in op_category.lower() or search_field in op_descr.lower():
            tmp.append(op)

    logger.debug(f"В поиск передано: {search_field}. Найдено совпадений: {len(tmp)}")

    return tmp


def search_by_persons(filepath: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция возвращает список операций физическим лицам
    :param filepath: путь до excel файла
    :return:
    """

    tmp = []
    op_data = read_file_data(filepath)

    for op in op_data:
        if op["Категория"] != "Переводы":
            continue

        regex_pattern = r"\w* [\w]{1}\."
        result = re.findall(regex_pattern, op["Описание"])
        if result:
            tmp.append(op)

    logger.debug(f"Найдено совпадений: {len(tmp)}")

    return tmp
