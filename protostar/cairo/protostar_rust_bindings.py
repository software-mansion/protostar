from typing import Optional
from contextlib import contextmanager

import rust_test_runner_bindings


class CairoBindingException(Exception):
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


def run_tests(input_path: str) -> list[str]:
    with handle_bindings_errors("run_tests"):
        tests_results = rust_test_runner_bindings.run_tests(  # pyright: ignore
            input_path
        )
        return tests_results


@contextmanager
def handle_bindings_errors(binding_name: str):
    try:
        yield
    except RuntimeError as ex:
        raise CairoBindingException(
            message=f"A runtime error occurred in binding {binding_name}: {str(ex)}"
        ) from ex
    except BaseException as ex:
        raise CairoBindingException(
            message=f"A unexpected type of error occurred in binding {binding_name}: {str(ex)}"
        ) from ex
