from typing import Any

from .protostar_argument import ProtostarArgument
from ..io import Messenger, JsonMessenger, HumanMessenger, LogColorProvider


class MessengerFactory:
    OUTPUT_ARGUMENTS = [
        ProtostarArgument(
            name="json",
            description="Print machine readable output in JSON format.",
            type="bool",
        )
    ]

    def __init__(self, log_color_provider: LogColorProvider):
        self._log_color_provider = log_color_provider

    def from_args(self, args: Any) -> Messenger:
        if args.json:
            return self.json()

        return self.human()

    def human(self):
        return HumanMessenger(self._log_color_provider)

    def json(self):
        return JsonMessenger()
