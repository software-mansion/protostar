from typing import Dict, Callable, Any


class DelayedBuilder:
    def __init__(self, callable_to_delay: Callable[..., Any]) -> None:
        super().__init__()
        self._callable = callable_to_delay

    def internal_build(self, exec_locals: Dict) -> Callable[..., Any]:
        return self._callable(exec_locals)
