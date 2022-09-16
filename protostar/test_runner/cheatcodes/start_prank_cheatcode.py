from typing import Any, Callable, Optional

from protostar.starknet.cheatcode import Cheatcode
from protostar.test_runner.test_environment_exceptions import CheatcodeException


class StartPrankCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "start_prank"

    def build(self) -> Callable[..., Any]:
        return self.start_prank

    def start_prank(
        self, caller_address: int, target_contract_address: Optional[int] = None
    ):
        target = (
            target_contract_address
            if target_contract_address
            else self.contract_address
        )
        if target in self.cheatable_state.pranked_contracts_map:
            raise CheatcodeException(
                self, f"Contract with address {target} has been already pranked"
            )
        self.cheatable_state.pranked_contracts_map[target] = caller_address

        def stop_started_prank():
            target = (
                target_contract_address
                if target_contract_address
                else self.contract_address
            )

            if target not in self.cheatable_state.pranked_contracts_map:
                raise CheatcodeException(
                    self, f"Contract with address {target} has not been pranked"
                )
            del self.cheatable_state.pranked_contracts_map[target]

        return stop_started_prank
