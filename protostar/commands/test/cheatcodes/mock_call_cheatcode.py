from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Callable, Dict, List, Optional, Type, Union

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.execute_entry_point_base import (
    ExecuteEntryPointBase,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.commands.test.starkware.cheatable_carried_state import (
    CheatableCarriedState,
)
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)
from protostar.commands.test.starkware.types import (
    AddressType,
    ClassHashType,
    SelectorType,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade


class MockCallMisusageException(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ContractPathMapperState(ABC):
    @abstractmethod
    def set_contract_address_to_contract_path(
        self, contract_address: AddressType, contract_path: Path
    ) -> None:
        ...

    @abstractmethod
    def get_contract_path_from_contract_address(
        self, contract_address: AddressType
    ) -> Optional[Path]:
        ...

    @abstractmethod
    def set_contract_address_to_class_hash(
        self, contract_address: AddressType, class_hash: ClassHashType
    ) -> None:
        ...

    @abstractmethod
    def get_class_hash_from_contract_path(
        self, contract_address: AddressType
    ) -> Optional[ClassHashType]:
        ...

    @abstractmethod
    def set_class_hash_to_contract_path(self, class_hash: ClassHashType) -> None:
        ...

    @abstractmethod
    def get_contract_path_from_class_hash(self, class_hash: ClassHashType) -> Path:
        ...


class MockedCallState(ABC):
    MockCallData = List[str]

    @abstractmethod
    def set_mock_data(
        self,
        contract_address: AddressType,
        fn_selector: SelectorType,
        ret_data: Optional[MockCallData],
    ) -> None:
        ...

    @abstractmethod
    def get_mock_data(
        self, contract_address: AddressType, fn_selector: SelectorType
    ) -> MockCallData:
        ...

    @abstractmethod
    def clear_mock_data(
        self, contract_address: AddressType, fn_selector: SelectorType
    ) -> None:
        ...


class MockCallCheatcode(CheatableSysCallHandler):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        execute_entry_point_cls: Type[ExecuteEntryPointBase],
        tx_execution_context: TransactionExecutionContext,
        state: CheatableCarriedState,
        caller_address: int,
        contract_address: int,
        starknet_storage: BusinessLogicStarknetStorage,
        general_config: CheatableStarknetGeneralConfig,
        initial_syscall_ptr: RelocatableValue,
        mocked_call_state: MockedCallState,
        contract_path_mapper_state: ContractPathMapperState,
        data_transformer_facade: DataTransformerFacade,
    ):
        super().__init__(
            execute_entry_point_cls=execute_entry_point_cls,
            tx_execution_context=tx_execution_context,
            state=state,
            caller_address=caller_address,
            contract_address=contract_address,
            starknet_storage=starknet_storage,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
        )
        self.mocked_call_state = mocked_call_state
        self.contract_path_mapper_state = contract_path_mapper_state
        self.data_transformer_facade = data_transformer_facade

    @property
    def name(self) -> str:
        return "mock_call"

    def mock_call(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: Union[
            List[int],
            Dict[
                DataTransformerFacade.ArgumentName,
                DataTransformerFacade.SupportedType,
            ],
        ],
    ) -> Callable:
        selector = get_selector_from_name(fn_name)
        if isinstance(ret_data, Mapping):
            contract_path = (
                self.contract_path_mapper_state.get_contract_path_from_contract_address(
                    contract_address
                )
            )
            if contract_path is None:
                raise MockCallMisusageException(
                    (
                        "Couldn't map the `contract_address` to the contract path."
                        "Is the `contract_address` valid?"
                    ),
                )
            # ret_data = DataTransformerFacade.from_contract_path(
            #     contract_path, self._starknet_compiler
            # ).build_from_python_transformer(fn_name, "outputs")(ret_data)

        self.mocked_call_state.set_mock_data(
            contract_address, fn_selector=selector, ret_data=None  # TODO
        )

        def clear_mock():
            pass

        return clear_mock
