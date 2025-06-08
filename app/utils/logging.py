# logger.py
import logging
import sys


def get_logger(name: str = "myapp", level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger con formato enriquecido.

    Args:
        name (str): Nombre del logger.
        level (int): Nivel de log (DEBUG, INFO, etc.).

    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar múltiples handlers si ya fue configurado
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
  