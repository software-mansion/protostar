from argparse import Namespace
from pathlib import Path
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.protostar_exception import ProtostarException
from protostar.contract_path_resolver import ContractPathResolver

from protostar.cairo.bindings import protostar_rust_bindings


class TestRustCommand(ProtostarCommand):
    def __init__(
        self,
        contract_path_resolver: ContractPathResolver,
    ):
        self._contract_path_resolver = contract_path_resolver

    @property
    def name(self) -> str:
        return "test-rust"

    @property
    def description(self) -> str:
        return "Executes cairo1 tests in rust."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar test-rust"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="path",
                description="A path to the tests that will be run",
                type="str",
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        contract_paths: dict[str, list[str]] = {}
        for (
            contract_name
        ) in self._contract_path_resolver.configuration_file.get_contract_names():
            contract_paths[contract_name] = [
                str(path)
                for path in self._contract_path_resolver.configuration_file.get_contract_source_paths(
                    contract_name
                )
            ]
        if args.path is None:
            raise ProtostarException("No tests provided")
        test_path = Path(str(args.path))
        assert test_path.exists(), f"no such test: { test_path }"
        await protostar_rust_bindings.run_tests(str(test_path), contract_paths)
