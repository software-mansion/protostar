from contextlib import asynccontextmanager
from logging import getLogger
from typing import Callable, Optional

from protostar.starknet import Cheatcode, CheatcodeException, SimpleReportedException
from protostar.testing.test_environment_exceptions import (
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    RevertableException,
)

logger = getLogger()


class ExpectRevertContext:
    def __init__(self):
        self._expected_error: Optional[RevertableException] = None

    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        if self._expected_error is not None:
            if (
                self._expected_error.error_type is None
                and not self._expected_error.error_messages
            ):
                raise CheatcodeException(
                    "expect_revert", "Protostar is already expecting an exception"
                )
            raise CheatcodeException(
                "expect_revert",
                f"Protostar is already expecting an exception matching the following error: "
                f"{self._expected_error}",
            )

        self._expected_error = expected_error

        def stop_expecting_revert():
            logger.warning(
                "The callback returned by the `expect_revert` is deprecated."
            )
            if self._expected_error is not None:
                raise SimpleReportedException("Expected a transaction to be reverted.")

        return stop_expecting_revert

    @asynccontextmanager
    async def test(self):
        try:
            yield
            if self._expected_error is not None:
                raise ExpectedRevertException(self._expected_error)
        except RevertableException as ex:
            if self._expected_error:
                if not self._expected_error.match(ex):
                    raise ExpectedRevertMismatchException(
                        expected=self._expected_error,
                        received=ex,
                    ) from ex
            else:
                raise ex
        finally:
            self._expected_error = None


class ExpectRevertCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        context: ExpectRevertContext,
    ) -> None:
        super().__init__(syscall_dependencies)
        self._context = context

    @property
    def name(self) -> str:
        return "expect_revert"

    def build(self) -> Callable:
        return self.expect_revert

    def expect_revert(
        self, error_type: Optional[str] = None, error_message: Optional[str] = None
    ):
        return self._context.expect_revert(
            RevertableException(error_type=error_type, error_message=error_message)
        )
