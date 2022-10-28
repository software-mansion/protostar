from pathlib import Path

import pkg_resources


def read_compiled_devnet_account_contract():
    account_contract_path_str = pkg_resources.resource_filename(
        "starknet_devnet",
        "accounts_artifacts/OpenZeppelin/0.5.0/Account.cairo/Account.json",
    )
    return Path(account_contract_path_str).read_text(encoding="utf-8")
