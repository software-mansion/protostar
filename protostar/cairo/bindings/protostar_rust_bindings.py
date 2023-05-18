from contextlib import contextmanager

import rust_test_runner_bindings

from .cairo_bindings_exception import CairoBindingException


async def run_tests(input_path: str, contract_paths: dict[str, list[str]]):
    with handle_bindings_errors("run_tests"):
        rust_test_runner_bindings.run_tests(  # pyright: ignore
            input_path, contract_paths
        )


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
