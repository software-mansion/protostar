import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from starknet_py.net.models import parse_address
from starknet_py.net.signer import BaseSigner
from typing_extensions import Protocol

from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    DeclareCheatcodeNetworkConfig,
    ValidatedDeclareCheatcodeNetworkConfig,
)
from protostar.migrator.migrator_contract_identifier_resolver import (
    MigratorContractIdentifierResolver,
)
from protostar.starknet import (
    Cheatcode,
    KeywordOnlyArgumentCheatcodeException,
    CheatcodeException,
)
from protostar.starknet_gateway.gateway_facade import (
    GatewayFacade,
    InputValidationException,
)
from protostar.starknet.data_transformer import CairoOrPythonData


class DeployCheatcodeNetworkConfig(DeclareCheatcodeNetworkConfig):
    pass


@dataclass
class ValidatedDeployCheatcodeNetworkConfig(ValidatedDeclareCheatcodeNetworkConfig):
    @classmethod
    def from_deploy_cheatcode_network_config(
        cls, config: Optional[DeployCheatcodeNetworkConfig]
    ) -> "ValidatedDeclareCheatcodeNetworkConfig":
        return super().from_declare_cheatcode_network_config(config)


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class MigratorDeployContractCheatcodeProtocol(Protocol):
    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def __call__(
        self,
        class_hash: Union[str, int],
        constructor_args: Optional[CairoOrPythonData] = None,
        abi_path: Optional[str] = None,
        salt: Optional[int] = None,
        *args: Any,
        config: Optional[Any] = None,
    ) -> DeployedContract:
        ...


class MigratorDeployContractCheatcode(Cheatcode):
    @dataclass
    class Config:
        signer: Optional[BaseSigner] = None
        token: Optional[str] = None
        account_address: Optional[Union[str, int]] = None

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        migrator_contract_identifier_resolver: MigratorContractIdentifierResolver,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._migrator_contract_identifier_resolver = (
            migrator_contract_identifier_resolver
        )

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> MigratorDeployContractCheatcodeProtocol:
        return self._deploy_contract

    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def _deploy_contract(
        self,
        class_hash: Union[str, int],
        constructor_args: Optional[CairoOrPythonData] = None,
        abi_path: Optional[str] = None,
        salt: Optional[int] = None,
        *args: Any,
        config: Optional[DeployCheatcodeNetworkConfig] = None,
    ) -> DeployedContract:
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = (
            ValidatedDeployCheatcodeNetworkConfig.from_deploy_cheatcode_network_config(
                config
            )
        )

        if abi_path and not Path(abi_path).is_file():
            raise CheatcodeException(self, f"{abi_path} is not a correct ABI file path")

        abi = None if not abi_path else json.loads(Path(abi_path).read_text("utf-8"))

        try:
            class_hash = (
                class_hash if isinstance(class_hash, int) else int(class_hash, 16)
            )
        except ValueError as v_err:
            raise CheatcodeException(
                self,
                f"Class hash has to be an integer or a hexadecimal string. Provided value: {class_hash}",
            ) from v_err

        account_address = self._config.account_address
        try:
            account_address = (
                parse_address(account_address) if account_address is not None else None
            )
        except ValueError as v_err:
            raise CheatcodeException(
                self,
                f"Account address has to be an integer or a hexadecimal string. Provided value: {class_hash}",
            ) from v_err

        try:
            response = asyncio.run(
                self._gateway_facade.deploy_via_udc(
                    class_hash=class_hash,
                    inputs=constructor_args,
                    abi=abi,
                    salt=salt,
                    wait_for_acceptance=validated_config.wait_for_acceptance,
                    max_fee=validated_config.max_fee,
                    signer=self._config.signer,
                    account_address=account_address,
                    token=self._config.token,
                )
            )
        except InputValidationException as ive:
            raise CheatcodeException(self, ive.message) from ive
        return DeployedContract(contract_address=response.address)
