import logging
import os

from config import LOGS_DIR


# noinspection NonAsciiCharacters
class Логгер:

    def __init__(self, имя_логгера: str, каталог_сохранения: str = LOGS_DIR, режим: str = "w", уровень: int = 10):

        self.логгер = logging.getLogger(имя_логгера)
        self.логгер.setLevel(уровень)
        self.обработчик = logging.FileHandler(
            str(os.path.join(каталог_сохранения, имя_логгера + ".log")), mode=режим, encoding="utf8"
        )
        self.форматтер = logging.Formatter("%(name)s - %(funcName)s: %(message)s")

        self.обработчик.setFormatter(self.форматтер)
        self.логгер.addHandler(self.обработчик)

    def на_дежурстве(self) -> logging.Logger:
        return self.логгер
