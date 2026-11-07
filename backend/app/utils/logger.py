import logging
import sys


def configure_logging(
    level: int = logging.INFO
) -> logging.Logger:

    app_logger = logging.getLogger("financial_research")

    app_logger.setLevel(level)
    app_logger.propagate = False

    # Prevent duplicate handlers during application reloads
    if not any(
        getattr(handler, "_financial_research_handler", False)
        for handler in app_logger.handlers
    ):

        console_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)

        console_handler._financial_research_handler = True

        app_logger.addHandler(console_handler)

    return app_logger


# Configure the main application logger
configure_logging()


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for an individual application module.
    """

    return logging.getLogger(
        f"financial_research.{module_name}"
    )