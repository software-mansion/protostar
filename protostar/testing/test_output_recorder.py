from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, Generator, Tuple, Union

OutputName = Union[str, Tuple[str, int]]
"""
Output name is a sequence of atomic strings, like ``"setup"`` or ``"test"``,
or ``("test", 1)``.
"""


def format_output_name(name: OutputName) -> str:
    if isinstance(name, str):
        return name
    return f"{name[0]}:{name[1]}"


@dataclass
class OutputRecorder:
    captures: Dict[OutputName, StringIO] = field(default_factory=dict)
    """
    Readonly.
    """

    def record(self, name: OutputName) -> StringIO:
        if name in self.captures:
            raise KeyError(f"Output {format_output_name(name)} is already recorded.")

        buffer = StringIO()
        self.captures[name] = buffer
        return buffer

    def get_captures(self) -> Dict[OutputName, str]:
        return {k: v.getvalue() for k, v in self.captures.items()}

    @contextmanager
    def redirect(self, name: OutputName) -> Generator[None, None, None]:
        with redirect_stdout(self.record(name)):
            yield

    def fork(self) -> "OutputRecorder":
        return deepcopy(self)
