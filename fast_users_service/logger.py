import sys

from loguru import logger


def configure(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
        + "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{extra[context]} {message}</level>",
        filter=lambda record: record["extra"].get("context", False),
        level=level,
        enqueue=True,
        backtrace=False,
        colorize=True,
    )
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
        + "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        filter=lambda record: not record["extra"].get("context", None) is not None,
        level=level,
        enqueue=True,
        backtrace=False,
        colorize=True,
    )
