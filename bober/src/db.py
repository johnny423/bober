from functools import wraps
from typing import Callable

from sqlalchemy.orm import Session


def commit(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = next(arg for arg in args if isinstance(arg, Session))
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    return wrapper
