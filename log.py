import logging
from logging import Logger

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(levelname)5s | %(name)30s @ %(lineno)4s ::: %(message)s")
)


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger
