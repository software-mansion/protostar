from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

_contextvar: ContextVar["ApiContext"] = ContextVar("api_context_holder")


@dataclass(frozen=True)
class ApiContext:
    protostar_version: str

    @contextmanager
    def activate(self):
        token = _contextvar.set(self)
        try:
            yield
        finally:
            _contextvar.reset(token)


def api_context() -> ApiContext:
    current = _contextvar.get(None)
    assert current is not None, "Scripting API context must be initialized."
    return current
