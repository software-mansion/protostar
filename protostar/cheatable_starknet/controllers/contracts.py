import collections
import copy
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from starkware.starknet.business_logic.execution.objects import CallType
from starkware.starknet.business_logic.execution.objects import Event as StarknetEvent
from starkware.python.utils import to_bytes, from_bytes
from starkware.starknet.business_logic.transaction.objects import InternalDeclare
from starkware.starknet.public.abi import CONSTRUCTOR_ENTRY_POINT_SELECTOR
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import get_abi, EventManager
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_class import EntryPointType, ContractClass

from protostar.cheatable_starknet.cheatables.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import Event
from protostar.starknet.selector import Selector
from protostar.starknet.abi import AbiType
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    DataTransformerException,
    CairoOrPythonData,
    CairoData,
    from_python_transformer,
)
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)

if TYPE_CHECKING:
    from protostar.cairo_testing.cairo_test_execution_state import (
        ContractsControllerState,
    )


class ContractsCheaterException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConstructorInputTransformationException(ContractsCheaterException):
    pass


class ConstructorInvocationException(ContractsCheaterException):
    pass


@dataclass(frozen=True)
class DeclaredContract:
    class_hash: int


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: list[int]
    contract_address: int
    class_hash: int
    salt: int


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class ContractsController:
    def __init__(
        self, state: "ContractsControllerState", cached_state: "CheatableCachedState"
    ):
        self._state = state
        self._cached_state = cached_state

    async def _transform_calldata_to_cairo_data_by_addr(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        class_hash = self._state.get_class_hash_from_address(contract_address)
        return await self._transform_calldata_to_cairo_data(
            class_hash=class_hash,
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
            contract_abi = self._state.get_contract_abi_from_class_hash(class_hash)
            transformer = from_python_transformer(contract_abi, function_name, "inputs")
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

        with self._cached_state.copy_and_apply() as state_copy:
            await tx.apply_state_updates(
                state=state_copy, general_config=starknet_config
            )

        abi = get_abi(contract_class=contract_class)
        self._register_event_metadata(abi)
        class_hash = tx.class_hash
        assert class_hash is not None
        await self._cached_state.set_contract_class(class_hash, contract_class)

        class_hash = from_bytes(class_hash)

        if contract_class.abi:
            self._state.bind_class_hash_to_contract_abi(
                class_hash=class_hash, contract_abi=contract_class.abi
            )

        return DeclaredClass(
            class_hash=class_hash,
            abi=get_abi(contract_class=contract_class),
        )

    def _register_event_metadata(self, abi: AbiType):
        # pylint: disable=protected-access
        for event_key, event_name in EventManager(abi=abi)._selector_to_name.items():
            self._state.bind_event_key_to_event_selector(
                key=event_key, event_selector=Selector(event_name)
            )
            self._state.bind_event_selector_to_event_abi(
                event_selector=Selector(event_name), event_abi=abi
            )

    async def deploy_prepared(self, prepared: PreparedContract) -> DeployedContract:
        await self._cached_state.deploy_contract(
            contract_address=int(prepared.contract_address),
            class_hash=to_bytes(prepared.class_hash),
        )

        contract_class = await self._cached_state.get_contract_class(
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
        with self._cached_state.copy_and_apply():
            call_info = await ExecuteEntryPoint.create(
                contract_address=contract_address,
                calldata=constructor_calldata,
                entry_point_selector=CONSTRUCTOR_ENTRY_POINT_SELECTOR,
                caller_address=0,
                entry_point_type=EntryPointType.CONSTRUCTOR,
                call_type=CallType.DELEGATE,
                class_hash=class_hash_bytes,
            ).execute_for_testing(
                state=self._cached_state,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(call_info.get_sorted_events())

    def _add_emitted_events(
        self,
        starknet_emitted_events: list[StarknetEvent],
    ):
        self._state.add_emitted_events(
            [
                Event(
                    from_address=Address(starknet_emitted_event.from_address),
                    data=starknet_emitted_event.data,
                    key=self._state.get_event_selector_from_event_key(
                        starknet_emitted_event.keys[0]
                    ),
                )
                for starknet_emitted_event in starknet_emitted_events
            ]
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
        contract_address = Address.from_class_hash(
            class_hash=declared.class_hash,
            salt=salt,
            constructor_calldata=constructor_calldata,
        )
        self._state.bind_contract_address_to_class_hash(
            address=contract_address, class_hash=declared.class_hash
        )
        return PreparedContract(
            constructor_calldata=constructor_calldata,
            contract_address=int(contract_address),
            class_hash=declared.class_hash,
            salt=salt,
        )

    async def call(
        self,
        contract_address: Address,
        entry_point_selector: Selector,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        cairo_calldata = await self._transform_calldata_to_cairo_data_by_addr(
            contract_address=contract_address,
            function_name=str(entry_point_selector),
            calldata=calldata,
        )
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=cairo_calldata,
            entry_point_selector=entry_point_selector,
        )
        tmp_cached_state = copy.deepcopy(self._cached_state)
        result = await entry_point.execute_for_testing(
            state=tmp_cached_state,
            general_config=StarknetGeneralConfig(),
        )
        return result.retdata

    async def invoke(
        self,
        entry_point_selector: Selector,
        contract_address: Address,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        cairo_calldata = await self._transform_calldata_to_cairo_data_by_addr(
            contract_address=contract_address,
            function_name=str(entry_point_selector),
            calldata=calldata,
        )
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=cairo_calldata,
            entry_point_selector=entry_point_selector,
        )
        with self._cached_state.copy_and_apply() as state_copy:
            call_info = await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(call_info.get_sorted_events())

    async def send_message_to_l2(
        self,
        selector: Selector,
        from_l1_address: Address,
        to_l2_address: Address,
        payload: Optional[CairoData] = None,
    ) -> None:
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=to_l2_address,
            calldata=[int(from_l1_address), *(payload or [])],
            caller_address=from_l1_address,
            entry_point_selector=selector,
            entry_point_type=EntryPointType.L1_HANDLER,
            call_type=CallType.DELEGATE,
            class_hash=await self._cached_state.get_class_hash_at(int(to_l2_address)),
        )
        with self._cached_state.copy_and_apply() as state_copy:
            call_info = await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(call_info.get_sorted_events())

    def prank(self, caller_address: Address, target_address: Address):
        self._state.set_pranked_address(
            target_address=target_address, pranked_address=caller_address
        )

    def cancel_prank(self, target_address: Address):
        self._state.remove_pranked_address(target_address)
