from hypothesis.errors import UnsatisfiedAssumption

from protostar.protostar_exception import ProtostarException
from protostar.commands.test.test_environment_exceptions import ReportedException


class FuzzingError(ProtostarException):
    pass


class HypothesisRejectException(ReportedException):
    def __init__(
        self, unsatisfied_assumption_exc: UnsatisfiedAssumption, *args: object
    ) -> None:
        self.unsatisfied_assumption_exc = unsatisfied_assumption_exc
        super().__init__(*args)

    # pylint: disable=pointless-string-statement
    """
    Hypothesis uses exceptions to handle `hypothesis.reject()` and `hypothesis.assume()`.
    This class is used to smuggle them through the Cairo VM.
    """
