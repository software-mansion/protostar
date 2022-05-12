import os
import re
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Generator, List, Optional, Pattern, cast

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)

from src.commands.test.test_suite import TestSuite
from src.protostar_exception import ProtostarException
from src.utils.starknet_compilation import StarknetCompiler


class TestCollectingException(ProtostarException):
    pass


@dataclass
class TestCollector:
    @dataclass(frozen=True)
    class Result:
        test_suites: List[TestSuite]
        test_cases_count: int

        def log(self, logger: Logger):
            if self.test_cases_count:
                result: List[str] = ["Collected"]
                suites_count = len(self.test_suites)
                if suites_count == 1:
                    result.append("1 suite,")
                else:
                    result.append(f"{suites_count} suites,")

                result.append("and")
                if self.test_cases_count == 1:
                    result.append("1 test case")
                else:
                    result.append(f"{self.test_cases_count} test cases")

                logger.info(" ".join(result))
            else:
                logger.warn("No cases found")

    def __init__(self, starknet_compiler: StarknetCompiler) -> None:
        self._starknet_compiler = starknet_compiler

    supported_test_suite_filename_patterns = [
        re.compile(r"^test_.*\.cairo"),
        re.compile(r"^.*_test.cairo"),
    ]

    def collect(
        self,
        target: Path,
        match_pattern: Optional[Pattern] = None,
        omit_pattern: Optional[Pattern] = None,
    ) -> "TestCollector.Result":
        target_function: Optional[str] = None
        if re.match(r"^.*\.cairo::.*", target.name):
            file_name, target_function = target.name.split("::")
            target = target.parent / file_name
            assert not target.is_dir()

        test_suite_paths = self._get_test_suite_paths(target)

        if match_pattern:
            test_suite_paths = filter(
                lambda file_path: cast(Pattern, match_pattern).match(str(file_path)),
                test_suite_paths,
            )
        if omit_pattern:
            test_suite_paths = filter(
                lambda file_path: not cast(Pattern, omit_pattern).match(str(file_path)),
                test_suite_paths,
            )

        test_suites: List[TestSuite] = []
        for test_suite in test_suite_paths:
            test_suites.append(self._build_test_suite(test_suite, target_function))

        non_empty_test_suites = list(
            filter(lambda test_file: (test_file.test_functions) != [], test_suites)
        )
        return TestCollector.Result(
            test_suites=non_empty_test_suites,
            test_cases_count=sum(
                [len(test_suite.test_functions) for test_suite in non_empty_test_suites]
            ),
        )

    @classmethod
    def is_test_suite(cls, filename: str) -> bool:
        return any(
            test_re.match(filename)
            for test_re in cls.supported_test_suite_filename_patterns
        )

    def _build_test_suite(
        self, file_path: Path, target_function: Optional[str]
    ) -> TestSuite:
        test_functions = self._collect_test_functions(file_path)
        if target_function:
            test_functions = [f for f in test_functions if f["name"] == target_function]
        return TestSuite(
            test_path=file_path,
            test_functions=test_functions,
        )

    def _get_test_suite_paths(self, target: Path) -> Generator[Path, None, None]:
        if not target.is_dir():
            yield target
            return
        for root, _, files in os.walk(target):
            test_suite_paths = [Path(root, file) for file in files]
            test_suite_paths = filter(
                lambda file: self.is_test_suite(file.name), test_suite_paths
            )
            for test_suite_path in test_suite_paths:
                yield test_suite_path

    def _collect_test_functions(self, file_path: Path) -> List[dict]:
        try:
            return self._starknet_compiler.get_functions(file_path, prefix="test_")
        except PreprocessorError as p_err:
            print(p_err)
            raise TestCollectingException("Failed to collect test cases") from p_err
