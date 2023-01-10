import collections
import copy
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

from typing_extensions import Self

from starkware.python.utils import to_bytes, from_bytes
from starkware.starknet.business_logic.transaction.objects import (
    InternalDeclare,
)
from starkware.starknet.public.abi import AbiType, get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import get_abi, EventManager
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.business_logic.execution.objects import CallType
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import (
    CONSTRUCTOR_ENTRY_POINT_SELECTOR,
    get_selector_from_name,
)
from starkware.starknet.services.api.contract_class import EntryPointType, ContractClass

from protostar.contract_types import (
    PreparedContract,
    DeclaredContract,
    DeployedContract,
)
from protostar.starknet.types import ClassHashType
from protostar.starknet.cheater import Cheater
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    DataTransformerException,
    CairoOrPythonData,
    CairoData,
    from_python_transformer,
)


if TYPE_CHECKING:
    from protostar.starknet.cheatable_cached_state import CheatableCachedState


class ContractsCheaterException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConstructorInputTransformationException(ContractsCheaterException):
    pass


class ConstructorInvocationException(ContractsCheaterException):
    pass


class ContractsCheater(Cheater):
    def __init__(self, state: "CheatableCachedState"):
        self.event_name_to_contract_abi_map: Dict[str, AbiType] = {}
        self.class_hash_to_contract_abi_map: Dict[ClassHashType, AbiType] = {}
        self.class_hash_to_contract_path_map: Dict[ClassHashType, Path] = {}
        self.contract_address_to_class_hash_map: Dict[Address, ClassHashType] = {}
        self.cheatable_state = state

    def copy(self) -> Self:
        return copy.copy(self)

    def apply(self, parent: Self) -> None:
        parent.event_name_to_contract_abi_map = {
            **parent.event_name_to_contract_abi_map,
            **self.event_name_to_contract_abi_map,
        }

        parent.class_hash_to_contract_path_map = {
            **parent.class_hash_to_contract_path_map,
            **self.class_hash_to_contract_path_map,
        }
        parent.class_hash_to_contract_abi_map = {
            **parent.class_hash_to_contract_abi_map,
            **self.class_hash_to_contract_abi_map,
        }
        parent.contract_address_to_class_hash_map = {
            **parent.contract_address_to_class_hash_map,
            **self.contract_address_to_class_hash_map,
        }

    async def _transform_calldata_to_cairo_data_by_addr(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        contract_address_int = int(contract_address)
        class_hash = await self.cheatable_state.get_class_hash_at(contract_address_int)
        return await self._transform_calldata_to_cairo_data(
            class_hash=from_bytes(class_hash, "big"),
            function_name=function_name,
            calldata=calldata,
        )

    async def _transform_calldata_to_cairo_data(
        self,
        class_hash: int,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        if isinstance(calldata, collections.Mapping):
            contract_class = await self.cheatable_state.get_contract_class(
                class_hash=to_bytes(class_hash, 32, "big")
            )
            assert contract_class.abi, f"No abi found for the contract at {class_hash}"

            transformer = from_python_transformer(
                contract_class.abi, function_name, "inputs"
            )
            try:
                return transformer(calldata)
            except DataTransformerException as dt_exc:
                raise ConstructorInputTransformationException(
                    f"There was an error while parsing the arguments for the function {function_name}:\n"
                    + f"{dt_exc.message}",
                ) from dt_exc
        return calldata or []

    async def declare_contract(
        self,
        contract_class: ContractClass,
    ):
        starknet_config = StarknetGeneralConfig()
        tx = InternalDeclare.create(
            contract_class=contract_class,
            chain_id=starknet_config.chain_id.value,
            sender_address=DEFAULT_DECLARE_SENDER_ADDRESS,
            max_fee=0,
            version=0,
            signature=[],
            nonce=0,
        )

        with self.cheatable_state.copy_and_apply() as state_copy:
            await tx.apply_state_updates(
                state=state_copy, general_config=starknet_config
            )

        abi = get_abi(contract_class=contract_class)
        self._add_event_abi_to_state(abi)
        class_hash = tx.class_hash
        assert class_hash is not None
        await self.cheatable_state.set_contract_class(class_hash, contract_class)

        class_hash = from_bytes(class_hash)

        if contract_class.abi:
            self.class_hash_to_contract_abi_map[class_hash] = contract_class.abi

        return DeclaredClass(
            class_hash=class_hash,
            abi=get_abi(contract_class=contract_class),
        )

    def bind_class_hash_to_contract_identifier(
        self, class_hash: ClassHashType, contract_identifier: str
    ):
        self.class_hash_to_contract_path_map[class_hash] = Path(contract_identifier)

    def _add_event_abi_to_state(self, abi: AbiType):
        event_manager = EventManager(abi=abi)
        self.cheatable_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in event_manager._selector_to_name.values():
            self.event_name_to_contract_abi_map[event_name] = abi

    async def deploy_prepared(self, prepared: PreparedContract) -> DeployedContract:
        await self.cheatable_state.deploy_contract(
            contract_address=int(prepared.contract_address),
            class_hash=to_bytes(prepared.class_hash),
        )

        contract_class = await self.cheatable_state.get_contract_class(
            class_hash=to_bytes(prepared.class_hash)
        )

        has_constructor = len(
            contract_class.entry_points_by_type[EntryPointType.CONSTRUCTOR]
        )
        if has_constructor:
            await self.invoke_constructor(prepared)
        elif not has_constructor and prepared.constructor_calldata:
            raise ConstructorInvocationException(
                "Tried to deploy a contract with constructor calldata, but no constructor was found.",
            )

        return DeployedContract(contract_address=prepared.contract_address)

    async def invoke_constructor(self, prepared: PreparedContract):
        await self._transform_calldata_to_cairo_data(
            class_hash=prepared.class_hash,
            function_name="constructor",
            calldata=prepared.constructor_calldata,
        )
        await self.execute_constructor_entry_point(
            class_hash_bytes=to_bytes(prepared.class_hash),
            constructor_calldata=prepared.constructor_calldata,
            contract_address=int(prepared.contract_address),
        )

    async def execute_constructor_entry_point(
        self,
        class_hash_bytes: bytes,
        constructor_calldata: List[int],
        contract_address: int,
    ):
        await ExecuteEntryPoint.create(
            contract_address=contract_address,
            calldata=constructor_calldata,
            entry_point_selector=CONSTRUCTOR_ENTRY_POINT_SELECTOR,
            caller_address=0,
            entry_point_type=EntryPointType.CONSTRUCTOR,
            call_type=CallType.DELEGATE,
            class_hash=class_hash_bytes,
        ).execute_for_testing(
            state=self.cheatable_state,
            general_config=StarknetGeneralConfig(),
        )

    async def prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: CairoOrPythonData,
        salt: int,
    ) -> PreparedContract:
        constructor_calldata = await self._transform_calldata_to_cairo_data(
            class_hash=declared.class_hash,
            function_name="constructor",
            calldata=constructor_calldata,
        )

        contract_address = calculate_contract_address_from_hash(
            salt=salt,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=0,
        )

        self.contract_address_to_class_hash_map[
            Address(contract_address)
        ] = declared.class_hash

        return PreparedContract(
            constructor_calldata=constructor_calldata,
            contract_address=contract_address,
            class_hash=declared.class_hash,
            salt=salt,
        )

    async def call(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        contract_address_int = int(contract_address)
        cairo_calldata = await self._transform_calldata_to_cairo_data_by_addr(
            contract_address=contract_address,
            function_name=function_name,
            calldata=calldata,
        )
        entry_point = ExecuteEntryPoint.create_for_testing(
            contract_address=contract_address_int,
            calldata=cairo_calldata,
            entry_point_selector=get_selector_from_name(function_name),
        )
        result = await entry_point.execute_for_testing(
            state=copy.deepcopy(self.cheatable_state),
            general_config=StarknetGeneralConfig(),
        )
        return result.retdata

    async def get_contract_class_at(self, contract_address: int) -> ContractClass:
        class_hash_bytes = await self.cheatable_state.get_class_hash_at(
            int(contract_address)
        )
        return await self.cheatable_state.get_contract_class(class_hash_bytes)

    async def invoke(
        self,
        function_name: str,
        contract_address: Address,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        contract_address_int = int(contract_address)
        if isinstance(calldata, collections.Mapping):
            contract_class = await self.get_contract_class_at(contract_address_int)
            assert (
                contract_class.abi
            ), f"No abi found for the contract at {contract_address}"

            transformer = from_python_transformer(
                contract_class.abi, function_name, "inputs"
            )
            cairo_calldata = transformer(calldata)
        else:
            cairo_calldata = calldata or []

        entry_point = ExecuteEntryPoint.create_for_testing(
            contract_address=contract_address_int,
            calldata=cairo_calldata,
            entry_point_selector=get_selector_from_name(function_name),
        )
        with self.cheatable_state.copy_and_apply() as state_copy:
            await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )
