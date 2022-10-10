from typing import Callable


def multiply_decorator(other_dec: Callable, args: list):
    def inner(func):
        current_fn = func
        if not args:
            return current_fn
        args.reverse()
        for arg in args:
            if isinstance(arg, dict):
                current_fn = other_dec(**arg)(current_fn)
            else:
                current_fn = other_dec(*arg)(current_fn)
        return current_fn

    return inner
