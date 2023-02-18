import logging

def loggingFmt():
    LOGGING_FORMAT = '[%(asctime)s] - [%(levelname)-8s] -  %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.INFO)
