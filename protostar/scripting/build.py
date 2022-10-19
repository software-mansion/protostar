from os import PathLike
from typing import Union

from starknet_py.net.client_models import ContractClass
from starknet_py.utils.sync.sync import make_sync

__all__ = (
    "ContractIdentifier",
    "ContractName",
    "ContractSourcePath",
    "build",
    "build_sync",
)

ContractName = str
ContractSourcePath = PathLike
ContractIdentifier = Union[ContractName, ContractSourcePath]


async def build(
    contract: ContractIdentifier,
    *,
    disable_hint_validation: bool = False,
) -> ContractClass:
    raise NotImplementedError


build_sync = make_sync(build)
