from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from typing_extensions import Literal

from protostar.io.log_color_provider import LogColorProvider


@dataclass
class StarknetRequest:
    AS_HEX = {"transaction_hash", "contract_address", "class_hash"}
    Action = Literal["DEPLOY", "DECLARE", "CALL", "INVOKE"]
    Payload = Dict[str, Union[None, str, int, List[int], List[str]]]

    action: Action
    payload: Payload
    response: Payload

    @staticmethod
    def prettify_data_flow(
        color_provider: Optional[LogColorProvider],
        direction: Literal["FROM_STARKNET", "TO_STARKNET"],
        action: Action,
    ):
        words: List[str] = []
        protostar_label = "Protostar"
        arrow = "→"
        starknet_label = "StarkNet"

        if direction == "FROM_STARKNET":
            arrow = "←"

        if color_provider:
            bold = color_provider.bold
            arrow = bold(arrow)
            if direction == "FROM_STARKNET":
                starknet_label = bold(starknet_label)
            else:
                protostar_label = bold(protostar_label)

        words.append(f"({protostar_label} {arrow} {starknet_label})")
        if color_provider:
            words.append(color_provider.bold(action))
        else:
            words.append(action)

        return " ".join(words)

    @staticmethod
    def prettify_payload(
        color_provider: Optional[LogColorProvider], payload: Payload
    ) -> str:
        lines: List[str] = []
        max_key_length = 0
        for key in payload:
            if len(key) > max_key_length:
                max_key_length = len(key)

        first_column_width = max(max_key_length, 20)
        for key, value in payload.items():
            if key in StarknetRequest.AS_HEX:
                value = f"0x{value:064x}"

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
