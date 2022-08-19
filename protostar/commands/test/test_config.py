from dataclasses import dataclass
from enum import Enum

from starkware.starknet.testing.contract import StarknetContract
from typing_extensions import Self

from protostar.utils.abi import has_function_parameters


class TestMode(Enum):
    STANDARD = 1
    FUZZ = 2

    # TODO(mkaput): Remove this in favor of setting mode explicitly by cheatcodes in setup hooks.
    @classmethod
    def infer_from_contract_function(
        cls, function_name: str, contract: StarknetContract
    ) -> Self:
        if has_function_parameters(contract.abi, function_name):
            return cls.FUZZ

        return cls.STANDARD


@dataclass
class TestConfig:
    mode: TestMode = TestMode.STANDARD

    fuzz_max_examples: int = 100
