from pathlib import Path

from protostar.io import LogColorProvider
from protostar.testing import (
    OutputName,
    format_output_name,
)

from protostar.starknet import ExceptionMetadata


def format_file_path(file_path: Path, log_color_provider: LogColorProvider) -> str:
    return log_color_provider.colorize("GRAY", str(file_path))


def format_execution_time_human(
    execution_time: float, log_color_provider: LogColorProvider
) -> str:
    return f"time={log_color_provider.bold(f'{execution_time:.2f}')}s"


def format_execution_time_structured(execution_time: float) -> str:
    return f"{execution_time:.2f}"


def format_stdout(
    captured_stdout: dict[OutputName, str], log_color_provider: LogColorProvider
) -> list[str]:
    result: list[str] = []
    if len(captured_stdout) == 0 or all(
        len(val) == 0 for _, val in captured_stdout.items()
    ):
        return []

    result.append(f"\n[{log_color_provider.colorize('CYAN', 'captured stdout')}]:\n")

    for name, value in captured_stdout.items():
        if value:
            result.append(
                f"[{format_output_name(name)}]:\n{log_color_provider.colorize('GRAY', value)}\n"
            )

    return result


def format_metadata(metadata: ExceptionMetadata) -> str:
    return f"[{metadata.name}]:\n{metadata.format()}"
