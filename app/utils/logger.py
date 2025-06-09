# logger.py
from logging import Logger, getLogger, StreamHandler, Formatter, INFO
import sys


def get_logger(name: str, level: int = INFO) -> Logger:
    """
    Configura y devuelve un logger con formato enriquecido.

    Args:
        name (str): Nombre del logger.
        level (int): Nivel de log (DEBUG, INFO, etc.).

    Returns:
        logging.Logger: Logger configurado.
    """
    logger = getLogger(name)
    logger.setLevel(level)

    # Evitar múltiples handlers si ya fue configurado
    if not logger.handlers:
        handler = StreamHandler(sys.stdout)
        formatter = Formatter(
            fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
