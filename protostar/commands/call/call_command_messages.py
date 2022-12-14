from dataclasses import dataclass

from protostar.io.log_color_provider import LogColorProvider
from protostar.io.output import StructuredMessage
from protostar.starknet_gateway.call import CallOutput


@dataclass
class SuccessfulCallMessage(StructuredMessage):
    call_output: CallOutput

    def format_human(self, fmt: LogColorProvider) -> str:
        return f"""\
{fmt.colorize("GREEN", "Call successful.")}
Response:
{self.call_output.cairo_data}
"""

    def format_dict(self) -> dict:
        return {}
