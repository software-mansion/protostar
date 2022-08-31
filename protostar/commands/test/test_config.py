from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from starkware.starknet.testing.contract import StarknetContract
from typing_extensions import Self

from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.commands.test.test_suite import TestCase
from protostar.commands.test.testing_seed import random_seed, Seed
from protostar.protostar_exception import ProtostarException
from protostar.utils.abi import has_function_parameters


class TestModeConversionException(ProtostarException):
    def __init__(self, from_mode: "TestMode", to_mode: "TestMode"):
        super().__init__(
            f"Cannot convert test case from {from_mode.pretty_name} to {to_mode.pretty_name}. "
            "Do not mix configuration cheatcodes specific to both modes in single test setup hooks."
        )


class TestMode(Enum):
    UNDETERMINED = 0
    STANDARD = 1
    FUZZ = 2

    @property
    def pretty_name(self) -> str:
        if self is self.UNDETERMINED:
            # Note: This should be an unreachable case, but because this property is used
            #   in exception constructors, a fallback value in exception message would be more
            #   informational in case of bugs.
            return "mode ?"

        if self is self.STANDARD:
            return "standard mode"

        if self is self.FUZZ:
            return "fuzzing mode"

        raise NotImplementedError("Unreachable.")

    def can_convert_to(self, to_mode: Self) -> bool:
        return (
            self is self.UNDETERMINED
            or self is to_mode
            or (
                (self, to_mode)
                in {
                    (self.STANDARD, self.FUZZ),
                }
            )
        )

    def convert_to(self, to_mode: Self) -> Self:
        if not self.can_convert_to(to_mode):
            raise TestModeConversionException(from_mode=self, to_mode=to_mode)

        return to_mode

    def determine(self, function_name: str, contract: StarknetContract) -> Self:
        return self or self.infer_from_contract_function(function_name, contract)

    @classmethod
    def infer_from_contract_function(
        cls, function_name: str, contract: StarknetContract
    ) -> Self:
        if has_function_parameters(contract.abi, function_name):
            return cls.FUZZ

        return cls.STANDARD

    def __bool__(self) -> bool:
        """
        ``UNDETERMINED`` is treated as ``False`` in if statements.
        """
        return self is not self.UNDETERMINED


@dataclass
class TestConfig:
    mode: TestMode = TestMode.UNDETERMINED
    seed: Seed = field(default_factory=random_seed)

    fuzz_max_examples: int = 100
    fuzz_declared_strategies: Dict[str, StrategyDescriptor] = field(
        default_factory=dict
    )

    def convert_mode_to(self, to_mode: TestMode):
        self.mode = self.mode.convert_to(to_mode)

    def determine_mode(self, test_case: TestCase, contract: StarknetContract):
        self.mode = self.mode.determine(
            function_name=test_case.test_fn_name, contract=contract
        )
