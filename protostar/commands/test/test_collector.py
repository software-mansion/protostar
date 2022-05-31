import os
import re
from dataclasses import dataclass
from fnmatch import fnmatch
from glob import glob
from logging import Logger
from pathlib import Path
from typing import Generator, List, Optional, Pattern, Set, cast

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)

from protostar.commands.test.test_suite import TestSuite
from protostar.protostar_exception import ProtostarException
from protostar.utils.starknet_compilation import StarknetCompiler


class TestCollectingException(ProtostarException):
    pass


@dataclass
class TestCollector:
    class Result:
        def __init__(self, test_suites: List[TestSuite]) -> None:
            self.test_suites = test_suites
            self.test_cases_count = sum(
                [len(test_suite.test_case_names) for test_suite in test_suites]
            )

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
                logger.warning("No cases found")

    def __init__(self, starknet_compiler: StarknetCompiler) -> None:
        self._starknet_compiler = starknet_compiler

    supported_test_suite_filename_patterns = [
        re.compile(r"^test_.*\.cairo"),
        re.compile(r"^.*_test.cairo"),
    ]

    def collect(
        self,
        target: Path,
        omit_pattern: Optional[Pattern] = None,
    ) -> "TestCollector.Result":
        target_test_case: Optional[str] = None
        if re.match(r"^.*\.cairo::.*", target.name):
            file_name, target_test_case = target.name.split("::")
            target = target.parent / file_name
            assert not target.is_dir()

        test_suite_paths = self._get_test_suite_paths(target)

        if omit_pattern:
            test_suite_paths = filter(
                lambda file_path: not cast(Pattern, omit_pattern).match(str(file_path)),
                test_suite_paths,
            )

        test_suites: List[TestSuite] = []
        for test_suite in test_suite_paths:
            test_suites.append(self._build_test_suite(test_suite, target_test_case))

        non_empty_test_suites = list(
            filter(lambda test_file: (test_file.test_case_names) != [], test_suites)
        )

        return TestCollector.Result(
            test_suites=non_empty_test_suites,
        )

    def collect_from_globs(
        self,
        glob_targets: List[str],
        omit_pattern: Optional[Pattern] = None,
    ) -> "TestCollector.Result":

        unique_test_suites: Set[TestSuite] = set()
        for glob_target in glob_targets:
            test_suite_filepaths: Set[str] = set()
            target_test_case_glob: Optional[str] = None
            valid_glob = glob_target
            if re.match(r"^.*\.cairo::.*", glob_target):
                valid_glob, target_test_case_glob = glob_target.split("::")

            test_suite_filepaths.update(
                self._find_test_suite_filepaths_from_glob(valid_glob)
            )

            if omit_pattern:
                test_suite_filepaths = set(
                    filter(
                        lambda filepath: not cast(Pattern, omit_pattern).match(
                            str(filepath)
                        ),
                        test_suite_filepaths,
                    )
                )

            test_suites: List[TestSuite] = []
            for test_suite in test_suite_filepaths:
                test_suites.append(
                    self._build_test_suite_from_test_case_glob(
                        Path(test_suite), target_test_case_glob
                    )
                )

            non_empty_test_suites = list(
                filter(lambda test_file: (test_file.test_case_names) != [], test_suites)
            )

            unique_test_suites.update(non_empty_test_suites)

        return TestCollector.Result(
            test_suites=list(unique_test_suites),
        )

    def _find_test_suite_filepaths_from_glob(self, glob_target: str) -> Set[str]:
        results: Set[str] = set()
        matches = glob(glob_target, recursive=True)
        for match in matches:
            path = Path(match)
            if path.is_dir():
                results.update(self._find_test_suite_filepaths_in_dir(path))
            elif path.is_file() and TestCollector.is_test_suite(path.name):
                results.add(match)
        return results

    # pylint: disable=no-self-use
    def _find_test_suite_filepaths_in_dir(self, path: Path) -> Set[str]:
        filepaths = set(glob(f"{path}/**/*.cairo", recursive=True))
        results: Set[str] = set()
        for filepath in filepaths:
            if TestCollector.is_test_suite(Path(filepath).name):
                results.add(filepath)
        return results

    def _build_test_suite_from_test_case_glob(
        self, file_path: Path, target_test_case_glob: Optional[str]
    ) -> TestSuite:
        preprocessed = self._preprocess_contract(file_path)
        test_case_names = self._collect_test_case_names(preprocessed)
        if target_test_case_glob:
            test_case_names = [
                test_case_name
                for test_case_name in test_case_names
                if fnmatch(test_case_name, target_test_case_glob)
            ]

        return TestSuite(
            test_path=file_path,
            test_case_names=test_case_names,
            preprocessed_contract=preprocessed,
            setup_state_fn_name=self._find_setup_state_hook_name(preprocessed),
        )

    @classmethod
    def is_test_suite(cls, filename: str) -> bool:
        return any(
            test_re.match(filename)
            for test_re in cls.supported_test_suite_filename_patterns
        )

    def _build_test_suite(
        self, file_path: Path, target_test_case_name: Optional[str]
    ) -> TestSuite:
        preprocessed = self._preprocess_contract(file_path)
        test_case_names = self._collect_test_case_names(preprocessed)
        if target_test_case_name:
            test_case_names = [
                test_case_name
                for test_case_name in test_case_names
                if test_case_name == target_test_case_name
            ]

        return TestSuite(
            test_path=file_path,
            test_case_names=test_case_names,
            preprocessed_contract=preprocessed,
            setup_state_fn_name=self._find_setup_state_hook_name(preprocessed),
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

    def _collect_test_case_names(
        self, preprocessed: StarknetPreprocessedProgram
    ) -> List[str]:
        return self._starknet_compiler.get_function_names(
            preprocessed, predicate=lambda fn_name: fn_name.startswith("test_")
        )

    def _find_setup_state_hook_name(
        self, preprocessed: StarknetPreprocessedProgram
    ) -> Optional[str]:
        function_names = self._starknet_compiler.get_function_names(
            preprocessed, predicate=lambda fn_name: fn_name == "setup_state"
        )
        return function_names[0] if len(function_names) > 0 else None

    def _preprocess_contract(self, file_path: Path) -> StarknetPreprocessedProgram:
        try:
            return self._starknet_compiler.preprocess_contract(file_path)
        except PreprocessorError as p_err:
            print(p_err)
            raise TestCollectingException("Failed to collect test cases") from p_err
