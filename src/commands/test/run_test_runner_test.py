import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.utils.config.project_test import make_mock_project

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_run_test_runner(mocker):
    libs_path = str(Path(current_directory, "examples"))
    contracts = {"main": ["examples/basic.cairo"]}
    mock_project = make_mock_project(mocker, contracts, libs_path)
    await run_test_runner(
        project=mock_project,
        tests_root=Path(current_directory, "examples"),
        omit=re.compile(r".*invalid.*"),
        cairo_paths=[],
    )
