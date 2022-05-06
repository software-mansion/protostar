from pathlib import Path

import pytest

from src.commands.test.reporter import TestingResult

CURRENT_DIR = Path(__file__).parent


# @pytest.mark.asyncio
# async def test_asserts():
#     results = await run_test_runner(
#         CURRENT_DIR,
#         cairo_paths=[Path(CURRENT_DIR, "..", "..", "..", "..", "cairo")],
#     )

#     testing_result = TestingResult.from_reporters(results)

#     assert len(testing_result.failed) == 0
#     assert len(testing_result.broken) == 0
