# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
from protostar.cairo_testing import CairoTestExecutionState
from protostar.cheatable_starknet.callable_hint_locals import (
    StoreHintLocal,
    InvokeHintLocal,
    CallHintLocal,
    DeployContractHintLocal,
    PrankHintLocal,
    RollHintLocal,
    WarpHintLocal,
    DeployHintLocal,
    PrepareHintLocal,
    DeclareHintLocal,
    StopWarpHintLocal,
    StopRollHintLocal,
    SendMessageToL2HintLocal,
    ExpectEventsHintLocal,
    LoadHintLocal,
)
from protostar.starknet import StarknetState
from protostar.cheatable_starknet.controllers import (
    StorageController,
    ContractsController,
    BlockInfoController,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import (
    ExpectEventsController,
)
from protostar.compiler import ProjectCompiler
from protostar.testing import Hook


class CairoSharedHintLocalFactory:
    def __init__(
        self,
        starknet_state: StarknetState,
        test_execution_state: CairoTestExecutionState,
        project_compiler: ProjectCompiler,
        test_finish_hook: Hook,
    ):
        self._starknet_state = starknet_state
        self.project_compiler = project_compiler
        self._test_finish_hook = test_finish_hook
        self._test_execution_state = test_execution_state

    def build_hint_locals(self) -> List[HintLocal]:
        block_info_controller = BlockInfoController(
            state=self._test_execution_state.block_info_controller_state,
        )
        contracts_controller = ContractsController(
            state=self._test_execution_state.contracts_controller_state,
            starknet_state=self._starknet_state,
        )
        storage_controller = StorageController(
            state=self._test_execution_state.contracts_controller_state,
            starknet_state=self._starknet_state,
        )

        declare_cheatcode = DeclareHintLocal(
            project_compiler=self.project_compiler,
            contracts_controller=contracts_controller,
        )
        prepare_cheatcode = PrepareHintLocal(
            contracts_controller=contracts_controller,
        )
        deploy_cheatcode = DeployHintLocal(
            contracts_controller=contracts_controller,
        )

        return [
            WarpHintLocal(block_info_controller=block_info_controller),
            RollHintLocal(block_info_controller=block_info_controller),
            StopWarpHintLocal(block_info_controller=block_info_controller),
            StopRollHintLocal(block_info_controller=block_info_controller),
            PrankHintLocal(contracts_controller=contracts_controller),
            SendMessageToL2HintLocal(contracts_controller=contracts_controller),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractHintLocal(
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallHintLocal(contracts_controller=contracts_controller),
            InvokeHintLocal(contracts_controller=contracts_controller),
            StoreHintLocal(storage_controller=storage_controller),
            LoadHintLocal(storage_controller=storage_controller),
            ExpectEventsHintLocal(
                controller=ExpectEventsController(
                    test_finish_hook=self._test_finish_hook,
                    test_execution_state=self._test_execution_state,
                    state=self._test_execution_state.contracts_controller_state,
                ),
            ),
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
