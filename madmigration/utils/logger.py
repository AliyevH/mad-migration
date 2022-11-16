import logging
import coloredlogs

def configure_logging(file_name: str):
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)

    logger.addHandler(consoleHandler)

    coloredlogs.install(level='DEBUG', logger=logger, fmt='%(levelname)s file: %(name)s line: %(lineno)d  -> %(message)s')

    return logger
