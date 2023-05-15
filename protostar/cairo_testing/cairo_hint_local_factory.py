# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
from protostar.cairo_testing import CairoTestExecutionState
from protostar.cheatable_starknet.callable_hint_locals import (
    StoreHintLocal,
    InvokeHintLocal,
    CallHintLocal,
    PrankHintLocal,
    StartRollHintLocal,
    StartWarpHintLocal,
    DeployHintLocal,
    PrepareHintLocal,
    DeclareCairo0HintLocal,
    DeclareHintLocal,
    StopWarpHintLocal,
    StopRollHintLocal,
    SendMessageToL2HintLocal,
    ExpectEventsHintLocal,
    LoadHintLocal,
    MockCallHintLocal,
    ExpectCallHintLocal,
    AssertExpectCallHintLocal,
    PrintHintLocal,
    StartSpoofHintLocal,
    StopPrankHintLocal,
)
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.controllers import (
    StorageController,
    ContractsController,
    BlockInfoController,
    ExpectCallController,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import (
    ExpectEventsController,
)
from protostar.compiler import Cairo0ProjectCompiler
from protostar.contract_path_resolver import ContractPathResolver
from protostar.testing import Hook


class CairoSharedHintLocalFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        cairo0_project_compiler: Cairo0ProjectCompiler,
        contract_path_resolver: ContractPathResolver,
        test_finish_hook: Hook,
        test_execution_state: CairoTestExecutionState,
    ):
        self.cheatable_state = cheatable_state
        self.cairo0_project_compiler = cairo0_project_compiler
        self.contract_path_resolver = contract_path_resolver
        self._test_finish_hook = test_finish_hook
        self._test_execution_state = test_execution_state

    def build_hint_locals(self) -> List[HintLocal]:
        block_info_controller = BlockInfoController(
            cheatable_state=self.cheatable_state
        )
        contracts_controller = ContractsController(cheatable_state=self.cheatable_state)
        storage_controller = StorageController(cheatable_state=self.cheatable_state)

        declare_cheatcode = DeclareHintLocal(
            contracts_controller=contracts_controller,
            contract_path_resolver=self.contract_path_resolver,
        )
        declare_cairo0_cheatcode = DeclareCairo0HintLocal(
            project_compiler=self.cairo0_project_compiler,
            contracts_controller=contracts_controller,
        )
        prepare_cheatcode = PrepareHintLocal(
            contracts_controller=contracts_controller,
        )
        deploy_cheatcode = DeployHintLocal(
            contracts_controller=contracts_controller,
        )

        expect_call_controller = ExpectCallController(
            cheatable_state=self._test_execution_state.cheatable_state,
        )
        expect_events_controller = ExpectEventsController(
            test_execution_state=self._test_execution_state,
            cheatable_state=self._test_execution_state.cheatable_state,
        )

        self._test_finish_hook.on(expect_call_controller.assert_no_expected_calls_left)
        self._test_finish_hook.on(
            expect_events_controller.compare_expected_and_actual_results
        )

        return [
            StartWarpHintLocal(block_info_controller=block_info_controller),
            StartRollHintLocal(block_info_controller=block_info_controller),
            StopWarpHintLocal(block_info_controller=block_info_controller),
            StopRollHintLocal(block_info_controller=block_info_controller),
            PrankHintLocal(contracts_controller=contracts_controller),
            StopPrankHintLocal(contracts_controller=contracts_controller),
            SendMessageToL2HintLocal(contracts_controller=contracts_controller),
            deploy_cheatcode,
            declare_cheatcode,
            declare_cairo0_cheatcode,
            prepare_cheatcode,
            CallHintLocal(
                contracts_controller=contracts_controller,
                expect_call_controller=expect_call_controller,
            ),
            InvokeHintLocal(contracts_controller=contracts_controller),
            StoreHintLocal(storage_controller=storage_controller),
            LoadHintLocal(storage_controller=storage_controller),
            ExpectEventsHintLocal(controller=expect_events_controller),
            MockCallHintLocal(controller=contracts_controller),
            ExpectCallHintLocal(controller=expect_call_controller),
            AssertExpectCallHintLocal(controller=expect_call_controller),
            PrintHintLocal(),
            StartSpoofHintLocal(),
        ]


class CairoSetupHintLocalFactory:
    def __init__(self, shared_hint_local_factory: CairoSharedHintLocalFactory):
        self._shared_hint_local_factory = shared_hint_local_factory

    def build_hint_locals(self) -> list[HintLocal]:
        return self._shared_hint_local_factory.build_hint_locals()


class CairoTestHintLocalFactory:
    def __init__(self, shared_hint_local_factory: CairoSharedHintLocalFactory):
        self._shared_hint_local_factory = shared_hint_local_factory

    def build_hint_locals(self) -> list[HintLocal]:
        return self._shared_hint_local_factory.build_hint_locals()
