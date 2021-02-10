import logging
import sys


class _MaxLevelFilter(object):
    def __init__(self, highest_log_level):
        self._highest_log_level = highest_log_level

    def filter(self, log_record):
        return log_record.levelno <= self._highest_log_level


def logging_setup():
    # A handler for low level logs that should be sent to STDOUT
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(_MaxLevelFilter(logging.WARNING))
    #
    # A handler for high level logs that should be sent to STDERR
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    # create console handler with a higher log level
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(_MaxLevelFilter(logging.WARNING))
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s | SDX-Worker | thread: %(thread)d | %(name)s: %(message)s')
    error_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)

    # create and configure main logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # add the handler to the logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.propagate = False