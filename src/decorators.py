import os
from functools import wraps
from typing import Callable

import pandas as pd

from config import DATA_DIR


class ReportSaver:

    @staticmethod
    def to_excel(file_name: str = "result_{func}.xls") -> Callable:
        """
        Декоратор для сохранения результатов в Excel файл.
        :param file_name: Имя файла, в который будет сохранен результат. По умолчанию result_{func}.xls
        :return: Обертка для функции
        """

        def wrapper(func: Callable) -> Callable:
            @wraps(func)
            def inner(*args: tuple, **kwargs: dict) -> pd.DataFrame:

                result: pd.DataFrame = func(*args, **kwargs)

                result.to_excel(
                    f"{os.path.join(DATA_DIR, file_name.format(func=func.__name__))}", index=False, engine="openpyxl"
                )

                return result

            return inner

        return wrapper
