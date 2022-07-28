from typing import Dict, Callable, Any


class DelayedBuilder:
    """
    DelayedBuilder constructor takes in a callable of form:
    Callable[[exec_locals], Callable[..., Any]]

    This callable's job is to create a cheatcode with any exec_locals needed.
    """

    def __init__(self, callable_to_delay: Callable[..., Any]) -> None:
        super().__init__()
        self._callable = callable_to_delay

    def internal_build(self, exec_locals: Dict) -> Callable[..., Any]:
        return self._callable(exec_locals)
