from typing import Literal


def cprint(
    text: str,
    text_color: Literal["black", "red", "green", "yellow", "blue", "violet", "cyan", "default"] = "default",
    bg_color: Literal["black", "red", "green", "yellow", "blue", "violet", "cyan", "white", "default"] = "default",
    text_style: Literal["bold", "curve", "underline", "default"] = "default",
    end: str = "\n",
) -> None:
    """
    Функция для стилизаций сообщений выводимых в консоль
    :param text: Передаваемый текст
    :param text_color: Цвет текста
    :param bg_color: Цвет заднего фона
    :param text_style: Стиль текста
    :param end: Символ в конце сообщения
    :return: None
    """

    # Словарь цветов текста, заднего фона, стиля текста
    colors = {
        "text": {
            "default": "",
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "violet": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
        },
        "bg": {
            "default": "",
            "black": "\033[40m",
            "red": "\033[41m",
            "green": "\033[42m",
            "yellow": "\033[43m",
            "blue": "\033[44m",
            "violet": "\033[45m",
            "cyan": "\033[46m",
            "white": "\033[47m",
        },
        "style": {"default": "", "bold": "\033[1m", "curve": "\033[3m", "underline": "\033[4m"},
    }

    # Выводим сообщение с заданными параметрами
    print(colors["text"][text_color] + colors["bg"][bg_color] + colors["style"][text_style] + text, end=end)

    # Сбрасываем цвета и стили
    print("\033[0m", end="")
