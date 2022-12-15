from pathlib import Path
from typing import Protocol, Optional, List, Any

import pytest

from protostar.testing import TestingSummary
from tests.integration.conftest import RunTestRunnerFixture


class RunCairoTestRunnerFixture(Protocol):
    async def __call__(
        self,
        path: Path,
        seed: Optional[int] = None,
        max_steps: Optional[int] = None,
        disable_hint_validation: bool = False,
        profiling: bool = False,
        cairo_path: Optional[List[Path]] = None,
        test_cases: Optional[List[str]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        ...


@pytest.fixture(name="run_pure_cairo_test_runner", scope="module")
def run_pure_cairo_test_runner_fixture(
    run_test_runner: RunTestRunnerFixture,
) -> RunCairoTestRunnerFixture:
    async def wrapped(*args: Any, **kwargs: Any):
        return await run_test_runner(*args, **kwargs, use_cairo_test_runner=True)

    return wrapped
