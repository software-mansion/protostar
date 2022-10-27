import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Callable, ContextManager, List, Optional, Set, Tuple, cast

import pkg_resources
import pytest
from pytest import TempPathFactory
from pytest_mock import MockerFixture
from starknet_py.constants import DEVNET_FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId, compute_address
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starkware.starknet.public.abi import AbiType
from typing_extensions import Protocol

from protostar.commands.test.test_command import TestCommand
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.starknet_gateway.gateway_facade import Wei
from protostar.testing import TestingSummary
from tests.conftest import DevnetAccount, run_devnet
from tests.integration.protostar_fixture import (
    ProtostarFixture,
    build_protostar_fixture,
)


@dataclass
class CairoTestCases:
    passed: Set[str]
    failed: Set[str]
    broken: Set[str]
    skipped: Set[str]

    def __repr__(self) -> str:
        passed = "[Passed]\n" + "\n".join(sorted(self.passed))
        failed = "[Failed]\n" + "\n".join(sorted(self.failed))
        broken = "[Broken]\n" + "\n".join(sorted(self.broken))
        skipped = "[Skipped]\n" + "\n".join(sorted(self.skipped))

        return "\n".join([passed, failed, broken, skipped])


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: Optional[List[str]] = None,
    expected_failed_test_cases_names: Optional[List[str]] = None,
    expected_broken_test_cases_names: Optional[List[str]] = None,
    expected_skipped_test_cases_names: Optional[List[str]] = None,  # Explicitly skipped
):
    expected_passed_test_cases_names = expected_passed_test_cases_names or []
    expected_failed_test_cases_names = expected_failed_test_cases_names or []
    expected_broken_test_cases_names = expected_broken_test_cases_names or []
    expected_skipped_test_cases_names = expected_skipped_test_cases_names or []

    passed_test_cases_names = set(
        passed_test_case.test_case_name for passed_test_case in testing_summary.passed
    )
    failed_test_cases_names = set(
        failed_test_case.test_case_name for failed_test_case in testing_summary.failed
    )
    broken_test_cases_names = set(
        broken_test_case.test_case_name for broken_test_case in testing_summary.broken
    )
    skipped_test_cases_names = set(
        skipped_test_case.test_case_name
        for skipped_test_case in testing_summary.skipped
    )

    for broken_test_case in testing_summary.broken_suites:
        for test_case_name in broken_test_case.test_case_names:
            broken_test_cases_names.add(test_case_name)

    actual = CairoTestCases(
        passed=passed_test_cases_names,
        failed=failed_test_cases_names,
        broken=broken_test_cases_names,
        skipped=skipped_test_cases_names,
    )

    expected = CairoTestCases(
        passed=set(expected_passed_test_cases_names),
        failed=set(expected_failed_test_cases_names),
        broken=set(expected_broken_test_cases_names),
        skipped=set(expected_skipped_test_cases_names),
    )

    assert actual == expected


@pytest.fixture(name="devnet_gateway_url", scope="session")
def devnet_gateway_url_fixture(devnet_port: int):
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


class RunCairoTestRunnerFixture(Protocol):
    async def __call__(
        self,
        path: Path,
        seed: Optional[int] = None,
        disable_hint_validation: bool = False,
        profiling: bool = False,
        cairo_path: Optional[List[Path]] = None,
        test_cases: Optional[List[str]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        ...


@pytest.fixture(name="log_color_provider", scope="module")
def log_color_provider_fixture() -> LogColorProvider:
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    return log_color_provider


@contextmanager
def empty_protostar_toml():
    toml_path = (Path(".") / "protostar.toml").resolve()
    lib_dir = (Path(".") / "lib").resolve()
    lib_dir.mkdir(exist_ok=True)
    with open(toml_path, mode="w+", encoding="utf-8") as file:
        file.write(
            """["protostar.project"]\nlibs_path="lib"\n["protostar.contracts"]"""
        )
    yield
    toml_path.unlink(missing_ok=True)
    if lib_dir.is_dir():
        lib_dir.rmdir()


@pytest.fixture(name="run_cairo_test_runner", scope="module")
def run_cairo_test_runner_fixture(
    session_mocker: MockerFixture, log_color_provider: LogColorProvider
) -> RunCairoTestRunnerFixture:
    async def run_cairo_test_runner(
        path: Path,
        seed: Optional[int] = None,
        disable_hint_validation: bool = False,
        profiling: bool = False,
        cairo_path: Optional[List[Path]] = None,
        test_cases: Optional[List[str]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        protostar_directory_mock = session_mocker.MagicMock()
        protostar_directory_mock.protostar_test_only_cairo_packages_path = Path()

        project_cairo_path_builder = cast(
            ProjectCairoPathBuilder, session_mocker.MagicMock()
        )
        project_cairo_path_builder.build_project_cairo_path_list = (
            lambda relative_cairo_path_list: relative_cairo_path_list
        )

        targets: List[str] = []
        if test_cases is None:
            targets.append(str(path))
        else:
            for test_case in test_cases:
                targets.append(f"{str(path)}::{test_case}")

        ignored_targets: Optional[List[str]] = None
        if ignored_test_cases:
            ignored_targets = [
                f"{str(path)}::{ignored_test_case}"
                for ignored_test_case in ignored_test_cases
            ]
        with empty_protostar_toml():
            return await TestCommand(
                project_root_path=Path(),
                protostar_directory=protostar_directory_mock,
                project_cairo_path_builder=project_cairo_path_builder,
                logger=getLogger(),
                log_color_provider=log_color_provider,
                active_profile_name=None,
                cwd=Path(),
            ).test(
                targets=targets,
                ignored_targets=ignored_targets,
                seed=seed,
                profiling=profiling,
                disable_hint_validation=disable_hint_validation,
                cairo_path=cairo_path or [],
            )

    return run_cairo_test_runner


class CreateProtostarProjectFixture(Protocol):
    def __call__(self) -> ContextManager[ProtostarFixture]:
        ...


@pytest.fixture(name="create_protostar_project", scope="module")
def create_protostar_project_fixture(
    session_mocker: MockerFixture,
    tmp_path_factory: TempPathFactory,
    signing_credentials: Tuple[str, str],
) -> CreateProtostarProjectFixture:
    @contextmanager
    def create_protostar_project():
        tmp_path = tmp_path_factory.mktemp("project_name")
        project_root_path = tmp_path
        cwd = Path().resolve()
        protostar = build_protostar_fixture(
            mocker=session_mocker,
            project_root_path=tmp_path,
            signing_credentials=signing_credentials,
        )
        project_name = "project_name"
        protostar.init_sync(project_name)

        project_root_path = project_root_path / project_name
        os.chdir(project_root_path)
        # rebuilding protostar fixture to reload configuration file
        yield build_protostar_fixture(
            mocker=session_mocker,
            project_root_path=project_root_path,
            signing_credentials=signing_credentials,
        )
        os.chdir(cwd)

    return create_protostar_project


GetAbiFromContractFixture = Callable[[str], AbiType]


@pytest.fixture(name="get_abi_from_contract", scope="module")
def get_abi_from_contract_fixture(
    create_protostar_project: CreateProtostarProjectFixture,
) -> GetAbiFromContractFixture:
    def get_abi_from_contract(contract_source_code: str) -> AbiType:
        with create_protostar_project() as protostar:
            protostar.create_files({"src/main.cairo": contract_source_code})
            protostar.build_sync()
            with open("build/main_abi.json") as f:
                abi = json.load(f)
                return abi

    return get_abi_from_contract


@pytest.fixture(name="gateway_client")
def gateway_client_fixture(devnet_gateway_url: str):
    return GatewayClient(
        devnet_gateway_url,
    )


class FeeContract:
    def __init__(self, predeployed_account_client: AccountClient) -> None:
        self._predeployed_account_client = predeployed_account_client

    async def transfer(self, recipient: int, amount: Wei):
        fee_contract = Contract(
            address=DEVNET_FEE_CONTRACT_ADDRESS,
            abi=self._get_abi(),
            client=self._predeployed_account_client,
        )

        res = await fee_contract.functions["transfer"].invoke(
            recipient=recipient, amount=amount, max_fee=int(1e20)
        )
        await res.wait_for_acceptance()

    def _get_abi(self):
        return [
            {
                "inputs": [
                    {"name": "recipient", "type": "felt"},
                    {"name": "amount", "type": "Uint256"},
                ],
                "name": "transfer",
                "outputs": [{"name": "success", "type": "felt"}],
                "type": "function",
            },
            {
                "members": [
                    {"name": "low", "offset": 0, "type": "felt"},
                    {"name": "high", "offset": 1, "type": "felt"},
                ],
                "name": "Uint256",
                "size": 2,
                "type": "struct",
            },
        ]


@dataclass
class PreparedDevnetAccount(DevnetAccount):
    class_hash: int


class DevnetAccountPreparator:
    def __init__(
        self,
        predeployed_account_client: AccountClient,
        fee_contract: FeeContract,
    ) -> None:
        self._predeployed_account_client = predeployed_account_client
        self._fee_contract = fee_contract

    async def prepare(self, salt: int) -> PreparedDevnetAccount:
        class_hash = await self._declare()
        key_pair = KeyPair.from_private_key(123)
        address = self._compute_address(
            class_hash=class_hash, public_key=key_pair.public_key, salt=salt
        )
        await self._prefund(address)
        return PreparedDevnetAccount(
            class_hash=class_hash,
            address=str(address),
            private_key=str(key_pair.private_key),
            public_key=str(key_pair.public_key),
            signer=StarkCurveSigner(
                account_address=address,
                key_pair=key_pair,
                chain_id=StarknetChainId.TESTNET,
            ),
        )

    async def _declare(self) -> int:
        account_contract_path_str = pkg_resources.resource_filename(
            "starknet_devnet",
            "accounts_artifacts/OpenZeppelin/0.5.0/Account.cairo/Account.json",
        )

        declare_tx = await self._predeployed_account_client.sign_declare_transaction(
            compiled_contract=Path(account_contract_path_str).read_text(
                encoding="utf-8"
            ),
            max_fee=int(1e16),
        )
        resp = await self._predeployed_account_client.declare(transaction=declare_tx)
        await self._predeployed_account_client.wait_for_tx(resp.transaction_hash)
        return resp.class_hash

    async def _prefund(self, account_address: int):
        await self._fee_contract.transfer(recipient=account_address, amount=int(1e15))

    def _compute_address(self, class_hash: int, public_key: int, salt: int) -> int:
        return compute_address(
            salt=salt,
            class_hash=class_hash,
            constructor_calldata=[public_key],
            deployer_address=0,
        )


@pytest.fixture
def devnet_account_preparator(
    gateway_client: GatewayClient, devnet_account: DevnetAccount
):
    predeployed_account_client = AccountClient(
        address=devnet_account.address,
        client=gateway_client,
        key_pair=KeyPair(
            private_key=int(devnet_account.private_key, base=0),
            public_key=int(devnet_account.public_key, base=0),
        ),
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    fee_contract = FeeContract(predeployed_account_client=predeployed_account_client)
    return DevnetAccountPreparator(predeployed_account_client, fee_contract)
