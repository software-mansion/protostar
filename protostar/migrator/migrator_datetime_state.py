from datetime import datetime as DateTime
from typing import Optional


class MigratorDateTimeState:
    def __init__(self) -> None:
        self._datetime: Optional[DateTime] = None

    def update_to_now(self):
        self._datetime = DateTime.now()

    def get_prefix(self) -> Optional[str]:
        if self._datetime is None:
            return self._datetime
        return DateTime.strftime(self._datetime, "%Y%m%d%H%M%S")
