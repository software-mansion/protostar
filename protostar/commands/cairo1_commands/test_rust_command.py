from argparse import Namespace
from pathlib import Path
from typing import Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.protostar_exception import ProtostarException

from protostar.cairo.bindings import protostar_rust_bindings


class TestRustCommand(ProtostarCommand):
    @property
    def name(self) -> str:
        return "test-rust"

    @property
    def description(self) -> str:
        return "Executes Cairo 1 tests with Rust implementation of Protostar."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar test-rust"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="path",
                description="A path to the file with tests that will be run",
                type="str",
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        if args.path is None:
            raise ProtostarException("No tests provided")
        test_path = Path(str(args.path))
        assert test_path.exists(), f"no such test: { test_path }"
        protostar_rust_bindings.run_tests(str(test_path))
