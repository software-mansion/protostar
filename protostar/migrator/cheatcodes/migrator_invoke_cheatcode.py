import asyncio
from dataclasses import dataclass
from typing import Optional
import logging

from starknet_py.net.client_errors import ClientError
from starknet_py.net.signer import BaseSigner
from typing_extensions import Required, Protocol

from protostar.migrator.cheatcodes import CheatcodeNetworkConfig
from protostar.starknet import (
    Cheatcode,
    CheatcodeException,
    KeywordOnlyArgumentCheatcodeException,
    SimpleReportedException,
)
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet_gateway import (
    ContractNotFoundException,
    GatewayFacade,
    UnknownFunctionException,
    Fee,
)


class SignedCheatcodeConfig(CheatcodeNetworkConfig):
    max_fee: Required[Fee]


@dataclass
class ValidatedSignedCheatcodeConfig:
    max_fee: Fee
    wait_for_acceptance: bool = False

    @classmethod
    def from_dict(
        cls, chatcode_name_provider, config: SignedCheatcodeConfig
    ) -> "ValidatedSignedCheatcodeConfig":
        if "max_fee" not in config.keys():
            raise CheatcodeException(
                chatcode_name_provider,
                "max_fee is required in config but has not been provided",
            )
        return cls(
            wait_for_acceptance=config.get("wait_for_acceptance", False),
            max_fee=config["max_fee"],
        )


class InvokeCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData],
        *args,
        config: SignedCheatcodeConfig,
    ) -> None:
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
        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "invoke"

    def build(self) -> InvokeCheatcodeProtocol:
        return self.invoke

    def invoke(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData],
        *args,
        config: SignedCheatcodeConfig,
    ):
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        if config.get("auto_estimate_fee"):
            self._logger.warning(
                'auto_estimate_fee is deprecated, please use max_fee = "auto" instead'
            )
        validated_config = ValidatedSignedCheatcodeConfig.from_dict(self, config)
        max_fee = validated_config.max_fee
        wait_for_acceptance = validated_config.wait_for_acceptance

        if max_fee != "auto" and max_fee <= 0:
            raise CheatcodeException(
                self,
                message="max_fee must be greater than 0.",
            )
        if not self._account_address:
            raise CheatcodeException(
                self,
                message="Account address is required for fetching nonce. "
                "Please either provide it in the function call, or with global account-address option.",
            )

        if not self._signer:
            raise CheatcodeException(
                self,
                message="Signing is required when using invoke. "
                "Please either provide CLI credentials or a custom signer in invoke call.",
            )
        try:
            asyncio.run(
                self._gateway_facade.invoke(
                    contract_address=contract_address,
                    function_name=function_name,
                    max_fee=max_fee,
                    inputs=inputs,
                    signer=self._signer,
                    account_address=self._account_address,
                    wait_for_acceptance=wait_for_acceptance,
                )
            )
        except (UnknownFunctionException, ContractNotFoundException) as err:
            raise CheatcodeException(self, message=err.message) from err
        except ClientError as err:
            raise SimpleReportedException(message=err.message) from err
