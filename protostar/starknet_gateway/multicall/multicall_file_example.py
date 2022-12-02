from typing import Union

MULTICALL_FILE_EXAMPLE = """[[call]]
# defines an contract address identifier
id = "my_contract"
type = "deploy"
class-hash = CONTRACT_CLASS_HASH
calldata = []

[[call]]
type = "invoke"
entrypoint-name = "increase_balance"

# contract-address accepts a contract address or an identifier
contract-address = "$my_contract"

# calldata accepts felts or identifiers
calldata = [42]
"""


def prepare_multicall_file_example(class_hash: Union[str, int]) -> str:
    return MULTICALL_FILE_EXAMPLE.replace("CONTRACT_CLASS_HASH", str(class_hash))
