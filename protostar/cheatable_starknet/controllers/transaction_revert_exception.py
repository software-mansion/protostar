import ast
from dataclasses import dataclass


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
