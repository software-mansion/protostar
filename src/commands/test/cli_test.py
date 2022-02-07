import re
from pathlib import Path

import pytest

from src.commands.test.test import test

current_directory = Path(__file__).parent


@pytest.mark.asyncio
async def test_cli():
    await test(
        sources_directory=Path(current_directory, "examples"),
        omit=re.compile(r".*invalid.*"),
        cairo_paths=[
            Path(current_directory, "examples"),
            Path(current_directory, "examples", "broken"),
        ],
    )
