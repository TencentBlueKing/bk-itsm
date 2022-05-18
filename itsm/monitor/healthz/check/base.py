# -*- coding: utf-8 -*-
from functools import wraps

checker_dict = {}


def checker(**kwargs):
    def decorator(func):
        """Deprecated decorator, please use :func:`celery.task`."""

        collect_metric = kwargs.get("collect_metric")
        checker_dict[collect_metric] = func

        @wraps(func)
        def _wrapped_view(*args, **kwargs):
            return func(*args, **kwargs)

        return _wrapped_view

    return decorator


def get_result(collect_metric):
    collect_func = checker_dict.get(collect_metric)
    if collect_func is None:
        return {}
    result, message = collect_func()

    return {"name": collect_metric, "value": result, "message": message}
