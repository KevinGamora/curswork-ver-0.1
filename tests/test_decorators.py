import os
import pandas as pd

from config import DATA_DIR
from src.decorators import ReportSaver


def test_decorator():
    """
    Тестирование функциональности декоратора для сохранения данных в Excel.
    """

    @ReportSaver.to_excel()
    def some_func():
        """
        Пример функции, возвращающей DataFrame для тестирования.
        """
        return pd.DataFrame({"Test01": [0], "Test02": [1]})

    some_func()  # Вызываем функцию, декорированную ReportSaver.to_excel()

    created_file_path = os.path.join(DATA_DIR, "result_some_func.xls")

    # Проверяем, что файл был создан
    assert os.path.exists(created_file_path)

    # Проверяем, что содержимое файла соответствует ожидаемым данным
    assert pd.read_excel(created_file_path).to_dict("records") == [{"Test01": 0, "Test02": 1}]

    # Удаляем созданный файл после выполнения теста
    os.remove(created_file_path)

    # Проверяем, что файл был удален
    assert not os.path.exists(created_file_path)
