import ast
from dataclasses import dataclass

from starkware.cairo.lang.compiler.test_utils import short_string_to_felt

from protostar.protostar_exception import ProtostarException


@dataclass
class TransactionRevertException(Exception):
    message: str
    raw_ex: Exception

    def get_panic_data(self) -> list[int]:
        msg = self.message.replace("Execution was reverted; failure reason:", "")
        if msg.startswith(" [") and msg.endswith("]."):
            msg = msg.replace(" [", "[")
            msg = msg.replace("].", "]")

            parsed_message_felts = ast.literal_eval(msg)
            return parsed_message_felts
        if len(msg) < 32:
            return [short_string_to_felt(msg)]
        raise ProtostarException(
            f"Panic data un-parseable, full exception:\n {self.raw_ex}"
        ) from self
