from pathlib import Path

from starknet_py.compile.compiler import Compiler


def compile_account_contract_with_validate_deploy() -> str:
    return Compiler(
        contract_source=(
            Path(__file__).parent / "account_contract_with_validate_deploy.cairo"
        ).read_text("utf-8"),
        is_account_contract=True,
    ).compile_contract()
