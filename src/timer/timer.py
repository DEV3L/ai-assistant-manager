import time
from functools import wraps

from loguru import logger


def timer(message: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 4)
            logger.debug(f"{message}: completed in {elapsed_time} seconds")
            return result

        return wrapper

    return decorator
