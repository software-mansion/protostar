from pathlib import Path
import os

from protostar.starknet import (
    StarknetPassManagerFactory,
    StarknetCompiler,
    StarknetCompilerConfig,
)

from starkware.cairo.lang.compiler.constants import LIBS_DIR_ENVVAR


def compile_account_contract_with_validate_deploy() -> str:
    contract = StarknetCompiler(
        config=StarknetCompilerConfig(
            include_paths=list(filter(None, os.getenv(LIBS_DIR_ENVVAR, "").split(":"))),
            disable_hint_validation=True,
        ),
        pass_manager_factory=StarknetPassManagerFactory,
    ).compile_contract(
        Path(__file__).parent / "account_contract_with_validate_deploy.cairo"
    )

    return contract.Schema().dumps(contract)
