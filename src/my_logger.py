import logging
import os

from config import LOGS_DIR


class Logger:

    def __init__(self, logger_name: str, save_dir: str = LOGS_DIR, mode: str = "w", level: int = 10):

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        self.handler = logging.FileHandler(
            str(os.path.join(save_dir, logger_name + ".log")), mode=mode, encoding="utf8"
        )
        self.formatter = logging.Formatter("%(name)s - %(funcName)s: %(message)s")

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def on_duty(self) -> logging.Logger:
        return self.logger
