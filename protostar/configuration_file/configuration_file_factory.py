from pathlib import Path
from typing import Optional

from .configuration_file import ConfigurationFile


class ConfigurationFileFactory:
    def __init__(self, cwd: Path) -> None:
        self._cwd = cwd

    def create(self) -> Optional[ConfigurationFile]:
        return None
