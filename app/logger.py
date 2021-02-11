import os
import sys

import structlog
import logging
from structlog import configure
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars, unbind_contextvars
from structlog.stdlib import LoggerFactory


class _MaxLevelFilter(object):
    def __init__(self, highest_log_level):
        self._highest_log_level = highest_log_level

    def filter(self, log_record):
        return log_record.levelno <= self._highest_log_level


def logging_config():

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(_MaxLevelFilter(logging.WARNING))

    logging.basicConfig(
        format='%(levelname)s | SDX-Worker | thread: %(thread)d | %(name)s: %('
               'message)s',
        level="INFO",
        handlers=[info_handler, error_handler]

    )

    configure(
        logger_factory=LoggerFactory(),
        processors=[
            structlog.stdlib.PositionalArgumentsFormatter(),
            merge_contextvars,
            structlog.processors.JSONRenderer()
        ],
    )
