import json
from dataclasses import dataclass

from protostar.io.log_color_provider import LogColorProvider
from protostar.io.output import StructuredMessage
from protostar.starknet_gateway.call import CallOutput


@dataclass
class SuccessfulCallMessage(StructuredMessage):
    call_output: CallOutput

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = []
        lines.append("[" + fmt.colorize("CYAN", "RAW RESULT") + "]")
        lines.append(fmt.bold(str(self.call_output.cairo_data)))
        lines.append("")
        lines.append("[" + fmt.colorize("CYAN", "TRANSFORMED RESULT") + "]")
        lines.append(fmt.bold(self._get_response_as_json()))
        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            "raw": self.call_output.cairo_data,
            "transformed": self.call_output.human_data,
        }

    def _get_response_as_json(self) -> str:
        return json.dumps(self.call_output.human_data, indent=4)
