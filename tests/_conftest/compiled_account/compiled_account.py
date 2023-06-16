from pathlib import Path

from protostar.starknet import (
    StarknetPassManagerFactory,
    StarknetCompiler,
    StarknetCompilerConfig,
)


def compile_account_contract_with_validate_deploy() -> str:
    return StarknetCompiler(
        config=StarknetCompilerConfig(
            include_paths=[],
            disable_hint_validation=True,
        ),
        pass_manager_factory=StarknetPassManagerFactory,
    ).compile_contract(
        Path(__file__).parent / "account_contract_with_validate_deploy.cairo"
    )
