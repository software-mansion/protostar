from protostar.protostar_exception import ProtostarException
from protostar.commands.test.test_environment_exceptions import ReportedException


class FuzzingError(ProtostarException):
    pass


class HypothesisRejectException(ReportedException):
    """
    Hypothesis uses exceptions to handle `hypothesis.reject()` and `hypothesis.assume()`.
    This class is used to smuggle them through the Cairo VM.
    """
