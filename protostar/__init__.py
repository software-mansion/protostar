import sys

from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash
from crypto_cpp_py.cpp_bindings import cpp_hash


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
