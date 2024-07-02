import datetime
import pandas as pd

def spending_by_category(transactions: pd.DataFrame, category: str, date: str | None = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)

    :param transactions: Принимает на вход DataFrame с транзакциями
    :param category: Искомая категория трат
    :param date: Опционально. Дата в формате День.Месяц.Год. Если не определена - текущая дата
    :return: DataFrame с отфильтрованными тратами по категории и дате
    """

    # Определяем дату, если она не передана. Используем текущую дату
    if not date:
        date = str(datetime.datetime.now()).rsplit(".", 1)[0]  # Отсекаем миллисекунды
        right_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    else:
        right_date = datetime.datetime.strptime(date, "%d.%m.%Y")

    # Определяем левую границу даты, соответствующую трем месяцам назад
    left_date = right_date - datetime.timedelta(hours=24 * 90)

    df = transactions
    # Преобразуем столбец с датами к формату datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтруем данные сначала по дате, затем по категории
    filtered_df = df.loc[df["Дата операции"].between(left_date.strftime("%Y-%m-%d"), right_date.strftime("%Y-%m-%d"))]
    filtered_df = filtered_df.loc[df["Категория"] == category]

    return filtered_df
