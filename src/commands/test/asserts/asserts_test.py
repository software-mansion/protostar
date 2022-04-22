from os import path
from pathlib import Path

import pytest
from src.commands.test.run_test_runner import run_test_runner

CURRENT_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts():
    results = await run_test_runner(
        CURRENT_DIR,
        cairo_paths=[Path(CURRENT_DIR, "..", "..", "..", "..", "cairo")],
    )

    assert sum([r.failed_count for r in results]) == 0
    assert sum([r.broken_count for r in results]) == 0
