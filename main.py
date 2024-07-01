from config import OP_DATA_DIR
from src.design import cprint
from src.reports import spending_by_category
from src.services import search_by_persons, simple_searching
from src.views import get_dataframe_from_file, post_events_response

if __name__ == "__main__":
    # Пример работы функции на запрос json для "Веб-страницы" - "Страница События"
    cprint(
        f"{' Пример работы функции для "Веб-страницы" - "Страница События" ':=^119}\n",
        text_color="yellow",
        text_style="bold",
    )

    print(post_events_response("1.10.2020", "ALL"))

    cprint(f"\n{' Конец работы функции ':=^119}\n", text_color="yellow", text_style="bold")

    # Пример работы функции для "Сервисы" - "Простой поиск"

    cprint(
        f"{' Пример работы функции для "Сервисы" - "Простой поиск" ':=^119}\n", text_color="yellow", text_style="bold"
    )

    print(simple_searching("Топливо", OP_DATA_DIR))

    cprint(f"\n{' Конец работы функции ':=^119}\n", text_color="yellow", text_style="bold")

    # Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам"

    cprint(
        f"{' Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам" ':=^119}\n",
        text_color="yellow",
        text_style="bold",
    )

    print(search_by_persons(OP_DATA_DIR))

    cprint(f"\n{' Конец работы функции ':=^119}\n", text_color="yellow", text_style="bold")

    # Пример работы функций для "Отчеты" - "Траты по категории"

    cprint(
        f"{' Пример работы функций для "Отчеты" - "Траты по категории" ':=^119}\n",
        text_color="yellow",
        text_style="bold",
    )

    df = get_dataframe_from_file(OP_DATA_DIR)
    print(spending_by_category(df, "Топливо", "15.02.2018"))

    cprint(f"\n{' Конец работы функции ':=^119}\n", text_color="yellow", text_style="bold")
