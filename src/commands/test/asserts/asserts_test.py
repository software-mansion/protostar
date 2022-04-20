from os import path
from pathlib import Path

import pytest
from src.commands.test.reporter import TestReporter
from src.commands.test.run_test_runner import run_test_runner
from src.commands.test.run_test_runner_test import all_passed

CURRENT_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts():
    result = await run_test_runner(
        CURRENT_DIR,
        cairo_paths=[Path(CURRENT_DIR, "..", "..", "..", "..", "cairo")],
    )

    assert all_passed(result)
