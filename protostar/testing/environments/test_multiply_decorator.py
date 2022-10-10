from typing import Callable
from .multiply_decorator import multiply_decorator


def test_multiply_decorator():
    decorator_call_count = [0]

    def sample_dec(additional_value: int):
        def decorator(target_fn: Callable) -> Callable:
            def inner(value: int) -> int:
                decorator_call_count[0] += 1
                return target_fn(additional_value + value)

            return inner

        return decorator

    @sample_dec(12)
    def sample_func(value: int) -> int:
        return value + 1

    assert sample_func(1) == 14
    assert decorator_call_count[0] == 1

    @multiply_decorator(sample_dec, [(1,), (2,), (3,)])
    def sample_func_multiply_decorator(value: int):
        return value + 1

    assert sample_func_multiply_decorator(2) == 9
    assert decorator_call_count[0] == 4
