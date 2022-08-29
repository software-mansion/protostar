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
        account_address: Optional[str] = None,
        auto_estimate_fee: bool = False,
        signer: Optional[BaseSigner] = None,
    ) -> Any:
        ...


class MigratorInvokeCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        global_account_address: Optional[str],
        global_signer: Optional[BaseSigner],
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._global_signer = global_signer
        self._global_account_address = global_account_address

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
        account_address: Optional[str] = None,
        auto_estimate_fee: bool = False,
        signer: Optional[BaseSigner] = None,
    ):
        if max_fee is not None and max_fee <= 0:
            raise CheatcodeException(self, "max_fee must be greater than 0.")
        if not max_fee and not auto_estimate_fee:
            raise CheatcodeException(
                self,
                message="Either max_fee or auto_estimate_fee argument is required.",
            )
        account_address = account_address or self._global_account_address
        if not account_address:
            raise CheatcodeException(
                self,
                "Account address is required for fetching nonce. "
                "Please either provide it in the function call, or with global account-address option.",
            )
        signer = signer or self._global_signer

        if not signer:
            raise CheatcodeException(
                self,
                "Signing is required when using invoke. "
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
                    signer=signer,
                    account_address=account_address,
                )
            )
        except (UnknownFunctionException, ContractNotFoundException) as err:
            raise CheatcodeException(self, err.message) from err
