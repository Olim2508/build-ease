import logging


def except_shell(errors=(Exception,), default_value='', need_to_logging=True):
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                if need_to_logging:
                    logging.error(e)
                return default_value or None
        return new_func
    return decorator
