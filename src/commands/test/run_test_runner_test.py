import re
from pathlib import Path

import pytest

from src.commands.test import run_test_runner
from src.utils.config.package_test import mock_package

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_run_test_runner(mocker):
    libs_path = str(Path(current_directory, "examples"))
    contracts = {"main": ["examples/basic.cairo"]}
    mock_pkg = mock_package(mocker, contracts, libs_path)
    await run_test_runner(
        pkg=mock_pkg,
        tests_root=Path(current_directory, "examples"),
        omit=re.compile(r".*invalid.*"),
        cairo_paths=[],
    )
