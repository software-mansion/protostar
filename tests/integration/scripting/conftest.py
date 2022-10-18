from pathlib import Path

import pytest
from typing_extensions import Protocol


class CreateScriptFixture(Protocol):
    def __call__(self, script: str) -> Path:
        ...


@pytest.fixture(name="create_script")
def create_script_fixture(tmp_path: Path) -> CreateScriptFixture:
    def writer(script: str) -> Path:
        script_path = tmp_path / "test_script.py"
        script_path.write_text(script, encoding="utf-8")
        return script_path

    return writer
