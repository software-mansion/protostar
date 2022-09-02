from hypothesis.errors import UnsatisfiedAssumption

from protostar.commands.test.test_environment_exceptions import (
    ReportedException,
    BreakingReportedException,
)


class FuzzingError(BreakingReportedException):
    pass


class SearchStrategyBuildError(FuzzingError):
    """
    Describes an error happening while building a search strategy. Fuzzer catches it and re-raises
    as ``FuzzingError`` with extra information about causing fuzz parameter.
    """


class HypothesisRejectException(ReportedException):
    """
    Hypothesis uses exceptions to handle ``hypothesis.reject()`` and ``hypothesis.assume()``.
    This class is used to smuggle them through the Cairo VM.
    """

    def __init__(
        self, unsatisfied_assumption_exc: UnsatisfiedAssumption, *args: object
    ) -> None:
        self.unsatisfied_assumption_exc = unsatisfied_assumption_exc
        super().__init__(*args)
