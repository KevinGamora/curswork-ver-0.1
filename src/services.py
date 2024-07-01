import re

from config import OP_DATA_DIR
from src.my_logger import Логгер
from src.utils import read_file_data

логгер = Логгер("services").на_дежурстве()


# noinspection NonAsciiCharacters
def простой_поиск(поле_поиска: str, путь_файла: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция для поиска операций по полю поиска в описании операции или в категории.
    :param поле_поиска: Строка для поиска.
    :param путь_файла: Путь до файла
    :return: Список подходящих по поиску операций.
    """

    поле_поиска = поле_поиска.lower()
    все_данные_оп = read_file_data(путь_файла)

    tmp = []
    for оп in все_данные_оп:
        категория_оп = оп["Категория"] or " "
        описание_оп = оп["Описание"] or " "

        if поле_поиска in категория_оп.lower() or поле_поиска in описание_оп.lower():
            tmp.append(оп)

    логгер.debug(f"В поиск передано: {поле_поиска}. Найдено совпадений: {len(tmp)}")

    return tmp


# noinspection NonAsciiCharacters
def поиск_по_лицам(путь_файла: str = OP_DATA_DIR) -> list[dict]:
    """
    Функция возвращает список операций физическим лицам
    :param путь_файла: путь до excel файла
    :return: Список операций
    """

    tmp = []
    данные_оп = read_file_data(путь_файла)

    for оп in данные_оп:
        if оп["Категория"] != "Переводы":
            continue

        регулярное_выражение = r"\w* [\w]{1}\."
        результат = re.findall(регулярное_выражение, оп["Описание"])
        if результат:
            tmp.append(оп)

    логгер.debug(f"Найдено совпадений: {len(tmp)}")

    return tmp
