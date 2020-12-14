"""
Logging function for DataPuisto in Google Cloud. Django standard approach not
working.
"""
import logging

import google.cloud.logging

formatter_name = 'normal'
handler_name = 'gc_datapuisto'

def configure(logging_dict):
    """Custom logging config for Google Cloud."""

    # Do formatters first - they don't refer to anything else
    formatters = logging_dict.get('formatters', {})
    for name in formatters:
        try:
            formatters[name] = configure_formatter(formatters[name])
            # formatter_name = name
        except Exception as e:
            raise ValueError('Unable to configure '
                             'formatter %r' % name) from e

    # Next, instantiate a client
    client = google.cloud.logging.Client()

    # handlers = logging_dict.get('handlers', {})
    # for name in handlers:
    #     handler_name = name
    # Next retrieve a Cloud Logging handler based on the environment
    # you're running in and integrate the handler with the
    # Python logging module.
    handler_1 = client.get_default_handler(name=handler_name)

    handler_1.setFormatter(formatters[formatter_name])
    
    handler_2 = logging.StreamHandler()
    handler_2.setFormatter(formatters[formatter_name])

    # Finally, do loggers
    loggers = logging_dict.get('loggers', {})
    for name in loggers:
        try:
            configure_logger(name, loggers[name], handler_1, handler_2)
        except Exception as e:
            raise ValueError('Unable to configure logger '
                             '%r' % name) from e

def configure_formatter(config):
    fmt = config.get('format', None)
    dfmt = config.get('datefmt', None)
    style = config.get('style', '%')

    return logging.Formatter(fmt, dfmt, style)

def configure_logger(name, config, handler_1, handler_2):
    """Configure a non-root logger from a dictionary."""
    logger = logging.getLogger(name)
    level = config.get('level', None)
    if level is not None:
        logger.setLevel(logging._checkLevel(level))
    propagate = config.get('propagate', None)
    if propagate is not None:
        logger.propagate = propagate
    logger.addHandler(handler_1)
    logger.addHandler(handler_2)
