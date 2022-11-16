from typing import Any, ContextManager, Callable

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

    def __init__(
        self,
        log_color_provider: LogColorProvider,
        activity_indicator: Callable[[str], ContextManager],
    ):
        self._log_color_provider = log_color_provider
        self._activity_indicator = activity_indicator

    def from_args(self, args: Any) -> Messenger:
        if args.json:
            return self.json()

        return self.human()

    def human(self):
        return HumanMessenger(
            log_color_provider=self._log_color_provider,
            activity_indicator=self._activity_indicator,
        )

    @staticmethod
    def json():
        return JsonMessenger()
