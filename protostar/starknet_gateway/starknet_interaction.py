from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from typing_extensions import Literal

from protostar.utils.log_color_provider import LogColorProvider


@dataclass
class StarknetInteraction:
    direction: Literal["TO_STARKNET", "FROM_STARKNET"]
    action: str
    payload: Optional[Dict[str, Union[None, str, int, List[int], List[str]]]]

    def prettify(self, color_provider: Optional[LogColorProvider]) -> str:

        lines: List[str] = []

        first_line_items: List[str] = []
        protostar_label = "Protostar"
        arrow = "→"
        starknet_label = "StarkNet"

        if self.direction == "FROM_STARKNET":
            arrow = "←"

        if color_provider:
            bold = color_provider.bold
            arrow = bold(arrow)
            if self.direction == "FROM_STARKNET":
                starknet_label = bold(starknet_label)
            else:
                protostar_label = bold(protostar_label)

        first_line_items.append(f"({protostar_label} {arrow} {starknet_label})")
        if color_provider:
            first_line_items.append(color_provider.bold(self.action))
        else:
            first_line_items.append(self.action)

        lines.append(" ".join(first_line_items))

        if self.payload:
            max_key_length = 0
            for key in self.payload:
                if len(key) > max_key_length:
                    max_key_length = len(key)

            first_column_width = max(max_key_length, 20)
            for key, value in self.payload.items():

                if color_provider:
                    colorize = color_provider.colorize
                    bold = color_provider.bold
                    lines.append(
                        colorize(
                            "GRAY",
                            f"  {key.ljust(first_column_width)} {bold(value)}",
                        )
                    )
                else:
                    lines.append(f"  {key.ljust(first_column_width)} {value}")

        return "\n".join(lines)
