import copy
from dataclasses import dataclass
from typing import List, Optional, cast, Tuple
import json

from starkware.starknet.business_logic.execution.objects import (
    CallType,
    CallInfo,
    ExecutionResourcesManager,
)
from starkware.starknet.business_logic.execution.objects import Event as StarknetEvent
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.business_logic.transaction.objects import InternalDeclare
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.public.abi import AbiType, CONSTRUCTOR_ENTRY_POINT_SELECTOR
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
    DeprecatedDeclare,
)
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import EventManager
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_class.contract_class import (
    EntryPointType,
    DeprecatedCompiledClass,
    ContractClass,
    CompiledClass,
)
from starkware.starknet.business_logic.utils import write_class_facts

from protostar.cheatable_starknet.cheatables.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)

from protostar.cheatable_starknet.controllers.expect_events_controller import Event
from protostar.starknet.selector import Selector
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import CairoData


def make_contract_class(sierra_compiled: str):
    sierra_compiled_dict = json.loads(sierra_compiled)
    sierra_compiled_dict.pop("sierra_program_debug_info", None)
    sierra_compiled_dict["abi"] = json.dumps(sierra_compiled_dict["abi"])

    return ContractClass.load(sierra_compiled_dict)


def make_compiled_class(casm_compiled: str):
    return CompiledClass.loads(casm_compiled)


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
class DeclaredSierraClass:
    class_hash: int
    abi: str


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int
    salt: int


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


@dataclass(frozen=True)
class CallResult:
    return_data: CairoData


class NonValidatedInternalDeclare(InternalDeclare):
    # pylint: disable=too-many-ancestors

    def to_external(self) -> DeprecatedDeclare:
        # It is not implemented in the InternalDeclare itself as wll
        raise NotImplementedError(
            "Cannot convert internal declare transaction to external object."
        )

    def run_validate_entrypoint(
        self,
        remaining_gas: int,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
    ) -> Tuple[Optional[CallInfo], int]:
        """
        This hack might interfere with other things

        By default, InternalDeclare has a quite complicated run_validate_entrypoint method
        that among other things verifies if the sender_address of the Declare transaction is of a deployed contract.
        There's no account in protostar internals so this validation will always fail. This hack completely removes
        any form of validation.
        """
        return None, remaining_gas


class ContractsController:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    async def declare_sierra_contract(
        self,
        contract_class: ContractClass,
        compiled_class: CompiledClass,
    ) -> DeclaredSierraClass:
        """
        Declare a sierra contract.

        @param contract_class: sierra compiled contract to be declared
        @param compiled_class: casm compiled contract to be declared
        @return: DeclaredSierraClass instance.
        """
        compiled_class_hash = compute_compiled_class_hash(compiled_class)

        starknet_config = StarknetGeneralConfig()
        tx = NonValidatedInternalDeclare.create(
            contract_class=contract_class,
            compiled_class_hash=compiled_class_hash,
            chain_id=starknet_config.chain_id.value,
            sender_address=DEFAULT_DECLARE_SENDER_ADDRESS,
            max_fee=0,
            version=2,
            signature=[],
            nonce=await self.cheatable_state.get_nonce_at(
                DEFAULT_DECLARE_SENDER_ADDRESS
            ),
        )

        with self.cheatable_state.copy_and_apply() as state_copy:
            await tx.apply_state_updates(
                state=state_copy, general_config=starknet_config
            )

        abi = contract_class.abi

        class_hash = tx.class_hash
        await write_class_facts(
            self.cheatable_state.state_reader.ffc,  # pyright: ignore
            contract_class,
            compiled_class,
        )

        await self.cheatable_state.set_contract_class(class_hash, compiled_class)

        return DeclaredSierraClass(class_hash=class_hash, abi=abi)

    async def declare_cairo0_contract(
        self,
        contract_class: DeprecatedCompiledClass,
    ) -> DeclaredClass:
        starknet_config = StarknetGeneralConfig()
        tx = InternalDeclare.create_deprecated(
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

        abi = contract_class.abi
        assert abi is not None

        self._add_event_abi_to_state(abi)
        class_hash = tx.class_hash
        assert class_hash is not None
        await self.cheatable_state.set_contract_class(class_hash, contract_class)

        self.cheatable_state.class_hash_to_contract_abi_map[class_hash] = abi

        return DeclaredClass(
            class_hash=class_hash,
            abi=abi,
        )

    def _add_event_abi_to_state(self, abi: AbiType):
        event_manager = EventManager(abi=abi)
        self.cheatable_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in event_manager._selector_to_name.values():
            self.cheatable_state.event_name_to_contract_abi_map[event_name] = abi

    async def deploy_prepared(self, prepared: PreparedContract) -> DeployedContract:
        await self.cheatable_state.deploy_contract(
            contract_address=int(prepared.contract_address),
            class_hash=prepared.class_hash,
        )

        contract_class = await self.cheatable_state.get_contract_class(
            class_hash=prepared.class_hash
        )

        has_constructor = len(
            contract_class.entry_points_by_type[EntryPointType.CONSTRUCTOR]
        )
        if has_constructor:
            await self._invoke_constructor(prepared)
        elif not has_constructor and prepared.constructor_calldata:
            raise ConstructorInvocationException(
                "No constructor was found",
            )

        return DeployedContract(contract_address=prepared.contract_address)

    async def _invoke_constructor(self, prepared: PreparedContract):
        await self.execute_constructor_entry_point(
            class_hash=prepared.class_hash,
            constructor_calldata=prepared.constructor_calldata,
            contract_address=int(prepared.contract_address),
        )

    async def execute_constructor_entry_point(
        self,
        class_hash: int,
        constructor_calldata: List[int],
        contract_address: int,
    ):
        with self.cheatable_state.copy_and_apply() as state:
            call_info = await self._create_pranked_entry_point(
                contract_address=Address(contract_address),
                calldata=constructor_calldata,
                entry_point_selector=Selector(CONSTRUCTOR_ENTRY_POINT_SELECTOR),
                entry_point_type=EntryPointType.CONSTRUCTOR,
                call_type=CallType.DELEGATE,
                class_hash=class_hash,
            ).execute_for_testing(
                state=self.cheatable_state,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(
                cast(CheatableCachedState, state), call_info.get_sorted_events()
            )

    def _add_emitted_events(
        self,
        cheatable_state: CheatableCachedState,
        starknet_emitted_events: List[StarknetEvent],
    ):
        cheatable_state.emitted_events.extend(
            [
                Event(
                    from_address=Address(starknet_emitted_event.from_address),
                    data=starknet_emitted_event.data,
                    key=Selector(
                        cheatable_state.event_selector_to_name_map[
                            starknet_emitted_event.keys[0]
                        ]
                    ),
                )
                for starknet_emitted_event in starknet_emitted_events
            ]
        )

    async def prepare(
        self,
        class_hash: int,
        constructor_calldata: List[int],
        salt: int,
    ) -> PreparedContract:
        contract_address = calculate_contract_address_from_hash(
            salt=salt,
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=0,
        )

        self.cheatable_state.contract_address_to_class_hash_map[
            Address(contract_address)
        ] = class_hash

        return PreparedContract(
            constructor_calldata=constructor_calldata,
            contract_address=contract_address,
            class_hash=class_hash,
            salt=salt,
        )

    async def call(
        self,
        contract_address: Address,
        entry_point_selector: Selector,
        calldata: Optional[CairoData] = None,
    ) -> CallResult:
        cairo_calldata = calldata or []
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=cairo_calldata,
            entry_point_selector=entry_point_selector,
        )
        state_copy = copy.deepcopy(self.cheatable_state)
        state_copy.expected_contract_calls = (
            self.cheatable_state.expected_contract_calls
        )
        result = await entry_point.execute_for_testing(
            state=state_copy,
            general_config=StarknetGeneralConfig(),
        )
        return CallResult(return_data=result.retdata)

    async def invoke(
        self,
        entry_point_selector: Selector,
        contract_address: Address,
        calldata: Optional[List[int]],
    ):
        entry_point = self._create_pranked_entry_point(
            contract_address=contract_address,
            calldata=calldata or [],
            entry_point_selector=entry_point_selector,
        )
        with self.cheatable_state.copy_and_apply() as state_copy:
            call_info = await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(
                cast(CheatableCachedState, state_copy), call_info.get_sorted_events()
            )

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
            class_hash=await self.cheatable_state.get_class_hash_at(int(to_l2_address)),
        )
        with self.cheatable_state.copy_and_apply() as state_copy:
            call_info = await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )
            self._add_emitted_events(
                cast(CheatableCachedState, state_copy), call_info.get_sorted_events()
            )

    def prank(self, caller_address: Address, target_address: Address):
        self.cheatable_state.set_pranked_address(
            target_address=target_address, pranked_address=caller_address
        )

    def cancel_prank(self, target_address: Address):
        self.cheatable_state.remove_pranked_address(target_address)

    def mock_call(
        self, target_address: Address, entrypoint: Selector, response: CairoData
    ):
        return self.cheatable_state.add_mocked_response(
            target_address, entrypoint, response
        )

    def _create_pranked_entry_point(
        self,
        contract_address: Address,
        calldata: List[int],
        entry_point_selector: Selector,
        entry_point_type: EntryPointType = EntryPointType.EXTERNAL,
        call_type: CallType = CallType.CALL,
        class_hash: Optional[int] = None,
    ) -> CheatableExecuteEntryPoint:
        return CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=calldata,
            entry_point_selector=entry_point_selector,
            entry_point_type=entry_point_type,
            call_type=call_type,
            class_hash=class_hash,
            caller_address=self.cheatable_state.get_pranked_address(contract_address),
        )
