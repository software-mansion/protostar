from typing import Union, Tuple, Dict
from io import StringIO
from dataclasses import dataclass, field

OutputName = Union[str, Tuple[str, int]]
"""
Output name is a sequence of atomic strings, like ``"setup"`` or ``"test"``,
or ``("test", 1)``.
"""


def format_output_name(name: OutputName) -> str:
    if isinstance(name, str):
        if name.startswith("test__"):
            return "test"
        return name
    if name[0].startswith("test__"):
        return f"test:{name[1]}"
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


# # In TestExecutionState
# class TestExecutionState:
#     output_recorder: OutputRecorder

#     # fork will copy output_recorder

# # Execution environments will wrap `await.perform_invoke` calls with:
# with redirect_stdout(self.state.output_recorder.record(...)):
#     ...
