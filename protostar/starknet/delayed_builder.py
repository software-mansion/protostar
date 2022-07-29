from typing import Dict, Callable, Any


class DelayedBuilder:
    """
    DelayedBuilder constructor takes in a callable of form:
    Callable[[exec_locals], Any]

    This callable's job is to create a cheatcode with any exec_locals needed.
    """

    def __init__(self, callable_to_delay: Callable[..., Any]) -> None:
        self._callable = callable_to_delay

    def internal_build(self, exec_locals: Dict) -> Any:
        return self._callable(exec_locals)
