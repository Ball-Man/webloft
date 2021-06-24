import logging

# Logging
LOGGING_FILE = 'webloft.log'
LOGGING_LEVEL = logging.DEBUG

logger = logging.getLogger()


def setup_logging():
    """Setup the loggers and log level for mile.
    See LOGGING_LEVEL and LOGGING_FILE.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                  '%Y-%m-%d %H:%M:%S')

    logger.setLevel(LOGGING_LEVEL)

    file_handler = logging.FileHandler(LOGGING_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
