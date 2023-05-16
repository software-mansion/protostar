from contextlib import contextmanager

import rust_test_runner_bindings

from .cairo_bindings_exception import CairoBindingException


def run_tests(input_path: str):
    with handle_bindings_errors("run_tests"):
        rust_test_runner_bindings.run_tests(input_path)  # pyright: ignore


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
