import logging.config


def configure_logging(*args, **kwargs):
    """Logging portable: no depende del registro de Windows ni de colores ANSI."""
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"plain": {"format": "[{levelname}] {name}: {message}", "style": "{"}},
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
        "loggers": {"django": {"handlers": ["console"], "level": "INFO", "propagate": False}},
    })
