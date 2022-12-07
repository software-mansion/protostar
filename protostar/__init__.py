import sys
from copy import copy
from typing import Any

from crypto_cpp_py.cpp_bindings import cpp_hash
from starkware.starknet.services.api.contract_class import ContractClass


def patched_pedersen_hash(left: int, right: int) -> int:
    return cpp_hash(left, right)


# This is a monkey-patch to improve the performance of the protostar tests
# We are using c++ code for calculating the pedersen hashes
# instead of python implementation from cairo-lang package
# It is placed before everything else to make sure only the patched function
# is used
setattr(
    sys.modules["starkware.crypto.signature.fast_pedersen_hash"],
    "pedersen_hash",
    patched_pedersen_hash,
)
setattr(
    sys.modules["starkware.cairo.lang.vm.crypto"],
    "pedersen_hash",
    patched_pedersen_hash,
)

# Deep copy of a ContractClass takes a lot of time, but it should never be mutated.
def shallow_copy(self: Any, memo: Any):  # pylint: disable=unused-argument
    """
    A dummy implementation of ContractClass.__deepcopy__
    """
    return copy(self)


setattr(ContractClass, "__deepcopy__", shallow_copy)

# Python complains about importing `Project`` if the import below is removed
# pylint: disable=C0413
from protostar.commands import (
    BuildCommand,
    InitCommand,
    InstallCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from protostar.start import main
