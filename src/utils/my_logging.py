import logging
import os


def setup_logger(
    name: str = "app_logger", log_file: str = "logs/app.log", level: int = logging.INFO
) -> logging.Logger:
    """
    Configures and returns a logger instance.

    :param name: Name of the logger.
    :param log_file: Path to the log file.
    :param level: Logging level.
    :return: Configured logger.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Example usage
# logger = setup_logger()
# logger.info("Logger initialized successfully.")
