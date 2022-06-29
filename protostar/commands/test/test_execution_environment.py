from copy import deepcopy
from logging import getLogger
from typing import Callable, List, Optional, Set

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.cheatcodes import (
    DeclareCheatcode,
    DeployCheatcode,
    DeployContractCheatcode,
    ExpectEventsCheatcode,
    ExpectRevertCheatcode,
    MockCallCheatcode,
    PrepareCheatcode,
    RollCheatcode,
    StartPrankCheatcode,
    WarpCheatcode,
)
from protostar.commands.test.starkware import (
    CheatableStarknetGeneralConfig,
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.starkware.forkable_starknet import ForkableStarknet
from protostar.commands.test.test_context import TestContext, TestContextHintLocal
from protostar.commands.test.test_environment_exceptions import (
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    RevertableException,
    SimpleReportedException,
    StarknetRevertableException,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.starknet_compilation import StarknetCompiler

logger = getLogger()


# pylint: disable=too-many-instance-attributes
class TestExecutionEnvironment:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        include_paths: List[str],
        forkable_starknet: ForkableStarknet,
        test_contract: StarknetContract,
        test_context: TestContext,
        starknet_compiler: StarknetCompiler,
    ):
        self.starknet = forkable_starknet
        self.test_contract: StarknetContract = test_contract
        self.test_context = test_context
        self._expected_error: Optional[RevertableException] = None
        self._include_paths = include_paths
        self._test_finish_hooks: Set[Callable[[], None]] = set()
        self._starknet_compiler = starknet_compiler

    @classmethod
    async def from_test_suite_definition(
        cls,
        starknet_compiler: StarknetCompiler,
        test_suite_definition: ContractClass,
        include_paths: Optional[List[str]] = None,
    ):
        general_config = CheatableStarknetGeneralConfig(
            cheatcodes_cairo_path=include_paths
        )  # type: ignore
        starknet = await ForkableStarknet.empty(general_config=general_config)

        starknet_contract = await starknet.deploy(contract_class=test_suite_definition)

        return cls(
            include_paths or [],
            forkable_starknet=starknet,
            test_contract=starknet_contract,
            test_context=TestContext(),
            starknet_compiler=starknet_compiler,
        )

    def fork(self):
        starknet_fork = self.starknet.fork()
        new_env = TestExecutionEnvironment(
            include_paths=self._include_paths,
            forkable_starknet=starknet_fork,
            test_contract=starknet_fork.copy_and_adapt_contract(self.test_contract),
            test_context=deepcopy(self.test_context),
            starknet_compiler=self._starknet_compiler,
        )
        return new_env

    async def invoke_setup_hook(self, fn_name: str) -> None:
        await self.invoke_test_case(fn_name)

    async def invoke_test_case(
        self, test_case_name: str
    ) -> Optional[ExecutionResourcesSummary]:
        execution_resources: Optional[ExecutionResourcesSummary] = None
        CheatableExecuteEntryPoint.cheatcode_factory = self._build_cheatcodes_factory()
        CheatableExecuteEntryPoint.custom_hint_locals = [
            TestContextHintLocal(self.test_context)
        ]

        try:
            execution_resources = await self._call_test_case_fn(test_case_name)
            for hook in self._test_finish_hooks:
                hook()
            if self._expected_error is not None:
                raise ExpectedRevertException(self._expected_error)
        except RevertableException as ex:
            if self._expected_error:
                if not self._expected_error.match(ex):
                    raise ExpectedRevertMismatchException(
                        expected=self._expected_error,
                        received=ex,
                    ) from ex
            else:
                raise ex
        finally:
            self._expected_error = None
            self._test_finish_hooks.clear()
        return execution_resources

    async def _call_test_case_fn(
        self, test_case_name: str
    ) -> ExecutionResourcesSummary:
        try:
            func = getattr(self.test_contract, test_case_name)
            tx_info: StarknetTransactionExecutionInfo = await func().invoke()
            return ExecutionResourcesSummary.from_execution_resources(
                tx_info.call_info.execution_resources
            )

        except StarkException as ex:
            raise StarknetRevertableException(
                error_message=StarknetRevertableException.extract_error_messages_from_stark_ex_message(
                    ex.message
                ),
                error_type=ex.code.name,
                code=ex.code.value,
                details=ex.message,
            ) from ex

    def add_test_finish_hook(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._test_finish_hooks.add(listener)

        def remove_hook():
            self._test_finish_hooks.remove(listener)

        return remove_hook

    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        if self._expected_error is not None:
            raise SimpleReportedException(
                f"Protostar is already expecting an exception matching the following error: {self._expected_error}"
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            logger.warning(
                "The callback returned by the `expect_revert` is deprecated."
            )
            if self._expected_error is not None:
                raise SimpleReportedException(
                    "Expected a transaction to be reverted before cancelling expect_revert"
                )

        return stop_expecting_revert

    def _build_cheatcodes_factory(self) -> CheatableExecuteEntryPoint.CheatcodeFactory:
        def build_cheatcodes(
            syscall_dependencies: Cheatcode.SyscallDependencies,
        ) -> List[Cheatcode]:
            data_transformer = DataTransformerFacade(self._starknet_compiler)
            declare_cheatcode = DeclareCheatcode(syscall_dependencies)
            prepare_cheatcode = PrepareCheatcode(syscall_dependencies, data_transformer)
            deploy_cheatcode = DeployCheatcode(syscall_dependencies)
            return [
                declare_cheatcode,
                prepare_cheatcode,
                deploy_cheatcode,
                DeployContractCheatcode(
                    syscall_dependencies,
                    declare_cheatcode,
                    prepare_cheatcode,
                    deploy_cheatcode,
                ),
                MockCallCheatcode(syscall_dependencies, data_transformer),
                WarpCheatcode(syscall_dependencies),
                RollCheatcode(syscall_dependencies),
                ExpectRevertCheatcode(
                    syscall_dependencies, testing_execution_environment=self
                ),
                StartPrankCheatcode(syscall_dependencies),
                ExpectEventsCheatcode(syscall_dependencies, self.starknet, self),
            ]

        return build_cheatcodes
