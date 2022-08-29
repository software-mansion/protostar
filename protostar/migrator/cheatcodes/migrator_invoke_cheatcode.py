import asyncio
from typing import Any, Optional

from starknet_py.net.signer import BaseSigner
from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import (
    ContractNotFoundException,
    GatewayFacade,
    UnknownFunctionException,
)
from protostar.utils.data_transformer import CairoOrPythonData


class InvokeCheatcodeProtocol(Protocol):
    # pylint: disable=too-many-arguments
    def __call__(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData] = None,
        max_fee: Optional[int] = None,
        auto_estimate_fee: bool = False,
    ) -> Any:
        ...


class MigratorInvokeCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        account_address: Optional[str],
        signer: Optional[BaseSigner],
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._signer = signer
        self._account_address = account_address

    @property
    def name(self) -> str:
        return "invoke"

    def build(self) -> InvokeCheatcodeProtocol:
        return self.invoke

    # pylint: disable=too-many-arguments
    def invoke(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData] = None,
        max_fee: Optional[int] = None,
        auto_estimate_fee: bool = False,
    ):
        if not isinstance(contract_address, int):
            raise CheatcodeException(
                self.name,
                message=f"contract_address must be an integer. got: {type(contract_address)}.",
            )
        if max_fee is not None and max_fee <= 0:
            raise CheatcodeException(
                self.name,
                message="max_fee must be greater than 0.",
            )
        if not max_fee and not auto_estimate_fee:
            raise CheatcodeException(
                self.name,
                message="Either max_fee or auto_estimate_fee argument is required.",
            )
        if not self._account_address:
            raise CheatcodeException(
                self.name,
                message="Account address is required for fetching nonce. "
                "Please either provide it in the function call, or with global account-address option.",
            )

        if not self._signer:
            raise CheatcodeException(
                self.name,
                message="Signing is required when using invoke. "
                "Please either provide CLI credentials or a custom signer in invoke call.",
            )
        try:
            return asyncio.run(
                self._gateway_facade.invoke(
                    contract_address=contract_address,
                    function_name=function_name,
                    max_fee=max_fee,
                    inputs=inputs,
                    auto_estimate_fee=auto_estimate_fee,
                    signer=self._signer,
                    account_address=self._account_address,
                )
            )
        except (UnknownFunctionException, ContractNotFoundException) as err:
            raise CheatcodeException(
                self.name,
                message=err.message,
            ) from err
