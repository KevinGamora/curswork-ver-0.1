import datetime

import pandas as pd


def spending_by_category(transactions: pd.DataFrame, category: str, date: str | None = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)

    :param transactions: Принимает на вход DataFrame
    :param category: Ищет, категорию среди переданных данных
    :param date: Опционально. Дата в формате День.Месяц.Год. Если не определена - текущая дата
    :return:
    """

    # Определняем дату в случае если её не передали. Берем текущую дату(сегодняшнюю)
    if not date:
        date = str(datetime.datetime.now()).rsplit(".", 1)[0]  # Отсекаем миллисекунды
        # Определяем "правый край" даты
        right_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    else:
        right_date = datetime.datetime.strptime(date, "%d.%m.%Y")

    # Определяем "левый край" даты, который соответсвует трём месяцем
    left_date = right_date - datetime.timedelta(hours=24 * 90)

    df = transactions
    # Определяем столбец с датами
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтруем сначала операции подходящие по дате. Далее по категории (разделен на 2 т.к. длинное выражение)
    filtered_df = df.loc[df["Дата операции"].between(left_date.strftime("%Y-%m-%d"), right_date.strftime("%Y-%m-%d"))]
    filtered_df = filtered_df.loc[df["Категория"] == category]

    return filtered_df
