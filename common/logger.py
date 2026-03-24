import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s",
    )


def get_logger(name: str):
    return logging.getLogger(name)
