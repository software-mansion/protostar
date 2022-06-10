from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Mapping, Optional, Union, cast

from protostar.commands.test.cheatcodes._cheatcode import Cheatcode
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)
from protostar.commands.test.starkware.types import AddressType
from protostar.utils.data_transformer_facade import DataTransformerFacade
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

if TYPE_CHECKING:
    from protostar.commands.test.test_execution_environment import (
        TestExecutionEnvironment,
    )


class DeployedContract:
    pass


class ContractCheatcode(Cheatcode):
    nonce = 1

    def __init__(
        self,
        testing_execution_environment: "TestExecutionEnvironment",
        cheatable_syscall_handler: "CheatableSysCallHandler",
    ) -> None:
        self._testing_execution_environment = testing_execution_environment
        self._cheatable_syscall_handler = cheatable_syscall_handler
        super().__init__()

    @property
    def name(self) -> str:
        return "Contract"

    def build(self) -> Callable:
        starknet_compiler = self._testing_execution_environment._starknet_compiler
        test_env = self._testing_execution_environment
        nonce = self.nonce
        self.nonce += 1

        class Contract:
            def __init__(
                self,
                contract_path: str,
                constructor_calldata: Optional[Union[List[int], Dict]] = None,
            ):
                self._contract_path = contract_path
                self._constructor_calldata = constructor_calldata
                self._declared = test_env.declare_in_env(self._contract_path)
                self._deployer_address = 111
                self._contract_address = self.calculate_contract_address()

            def calculate_contract_address(self):
                return calculate_contract_address_from_hash(
                    salt=cast(int, nonce),
                    class_hash=self._declared.class_hash,
                    constructor_calldata=self._constructor_calldata,
                    deployer_address=self.contract_address,
                )

            @property
            def class_hash(self) -> int:
                return self._declared.class_hash

            @property
            def contract_address(self) -> AddressType:
                return self._contract_address

            def deploy(self):
                assert not self._deployed  # TODO error
                if isinstance(self._constructor_calldata, Mapping):
                    fn_name = "constructor"
                    constructor_calldata = DataTransformerFacade.from_contract_path(
                        Path(self._contract_path), starknet_compiler
                    ).from_python(fn_name, **self._constructor_calldata)
                else:
                    constructor_calldata = self._constructor_calldata
                test_env.deploy_in_env(self._contract_path, constructor_calldata)
                # TODO add return

        return Contract
