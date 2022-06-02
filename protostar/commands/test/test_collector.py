import os
import re
from dataclasses import dataclass
from fnmatch import fnmatch
from glob import glob
from logging import Logger
from pathlib import Path
from typing import Dict, Generator, List, Optional, Pattern, Set, cast

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)

from protostar.commands.test.test_suite import TestSuite
from protostar.protostar_exception import ProtostarException
from protostar.utils.starknet_compilation import StarknetCompiler

TestSuiteGlob = str
TestSuiteFilepath = str
TestCaseGlob = str
Target = str
"""e.g. `tests/**/::test_*`"""
TestCasesDict = Dict[TestSuiteFilepath, Set[TestCaseGlob]]


@dataclass(frozen=True)
class ParsedTarget:
    test_suite_glob: Optional[TestCaseGlob]
    test_case_glob: Optional[TestCaseGlob]

    @classmethod
    def from_target(
        cls, target: Target, default_test_suite_glob: Optional[TestSuiteGlob]
    ):
        test_suite_glob: Optional[TestSuiteGlob] = target
        test_case_glob: Optional[TestCaseGlob] = None
        if "::" in target:
            (test_suite_glob, test_case_glob) = target.split("::")
        test_suite_glob = test_suite_glob or default_test_suite_glob
        return cls(test_suite_glob, test_case_glob)


@dataclass
class TargetTestCasesInfo:
    test_case_globs: Set[TestCaseGlob]
    ignored_test_case_globs: Set[TestCaseGlob]


TargetTestCasesInfoDict = Dict[TestSuiteFilepath, TargetTestCasesInfo]


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

    def __init__(
        self,
        starknet_compiler: StarknetCompiler,
        default_test_suite_glob: Optional[str] = None,
    ) -> None:
        self._starknet_compiler = starknet_compiler
        self._default_test_suite_glob = default_test_suite_glob

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
            setup_fn_name=self._find_setup_hook_name(preprocessed),
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

    def _find_setup_hook_name(
        self, preprocessed: StarknetPreprocessedProgram
    ) -> Optional[str]:
        function_names = self._starknet_compiler.get_function_names(
            preprocessed, predicate=lambda fn_name: fn_name == "__setup__"
        )
        return function_names[0] if len(function_names) > 0 else None

    def _preprocess_contract(self, file_path: Path) -> StarknetPreprocessedProgram:
        try:
            return self._starknet_compiler.preprocess_contract(file_path)
        except PreprocessorError as p_err:
            print(p_err)
            raise TestCollectingException("Failed to collect test cases") from p_err

    def collect_from_globs(
        self,
        globs: List[str],
        ignored_globs: Optional[List[str]] = None,
    ) -> "TestCollector.Result":
        parsed_targets = self.parse_targets(set(globs))
        ignored_parsed_targets = self.parse_targets(set(ignored_globs or []))

        test_cases_dict = self.build_test_cases_dict(parsed_targets)
        ignored_test_cases_dict = self.build_test_cases_dict(ignored_parsed_targets)

        filtered_test_cases_dict = self.filter_out_ignored_test_suites(
            test_cases_dict,
            ignored_test_cases_dict,
        )

        target_test_cases_info_dict = self.build_target_test_cases_info_dict(
            filtered_test_cases_dict,
            ignored_test_cases_dict,
        )

        test_suites = self._build_test_suites_from_target_test_cases_info_dict(
            target_test_cases_info_dict
        )

        non_empty_test_suites = list(
            filter(lambda test_file: (test_file.test_case_names) != [], test_suites)
        )

        return TestCollector.Result(
            test_suites=non_empty_test_suites,
        )

    def build_test_cases_dict(
        self,
        parsed_targets: Set[ParsedTarget],
    ) -> TestCasesDict:
        results: TestCasesDict = {}

        for parsed_target in parsed_targets:
            if not parsed_target.test_suite_glob:
                continue
            test_suite_filepaths = self._find_test_suite_filepaths_from_glob(
                parsed_target.test_suite_glob
            )
            for test_suite_filepath in test_suite_filepaths:
                test_case_globs = results.setdefault(test_suite_filepath, set())
                if parsed_target.test_case_glob:
                    test_case_globs.add(parsed_target.test_case_glob)

        return results

    def parse_targets(self, targets: Set[Target]) -> Set[ParsedTarget]:
        return {
            ParsedTarget.from_target(target, self._default_test_suite_glob)
            for target in targets
        }

    # pylint: disable=no-self-use
    def filter_out_ignored_test_suites(
        self,
        test_cases_dict: TestCasesDict,
        ignored_test_cases_dict: TestCasesDict,
    ):
        result = test_cases_dict.copy()
        for ignored_target_path in ignored_test_cases_dict:
            if (
                len(ignored_test_cases_dict[ignored_target_path]) == 0
                and ignored_target_path in result
            ):
                del result[ignored_target_path]
        return result

    # pylint: disable=no-self-use
    def build_target_test_cases_info_dict(
        self,
        test_cases_dict: TestCasesDict,
        ignored_test_cases_dict: TestCasesDict,
    ) -> TargetTestCasesInfoDict:
        result: TargetTestCasesInfoDict = {}
        for test_suite_filepath in test_cases_dict:
            target_test_cases_info = result.setdefault(
                test_suite_filepath,
                TargetTestCasesInfo(
                    test_case_globs=set(), ignored_test_case_globs=set()
                ),
            )
            target_test_cases_info.test_case_globs = test_cases_dict[
                test_suite_filepath
            ]
            if test_suite_filepath in ignored_test_cases_dict:
                target_test_cases_info.ignored_test_case_globs = (
                    ignored_test_cases_dict[test_suite_filepath]
                )
        return result

    def _find_test_suite_filepaths_from_glob(self, test_suite_glob: str) -> Set[str]:
        results: Set[str] = set()
        matches = glob(test_suite_glob, recursive=True)
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

    def _build_test_suites_from_target_test_cases_info_dict(
        self,
        target_test_cases_info_dict: TargetTestCasesInfoDict,
    ) -> List[TestSuite]:
        test_suites: List[TestSuite] = []
        for (
            test_suite_filepath,
            target_test_cases_info,
        ) in target_test_cases_info_dict.items():
            test_suites.append(
                self._build_test_suite_from_test_cases_info(
                    Path(test_suite_filepath),
                    target_test_cases_info,
                )
            )
        return test_suites

    def _build_test_suite_from_test_cases_info(
        self,
        test_suite_path: Path,
        test_cases_info: TargetTestCasesInfo,
    ) -> TestSuite:
        preprocessed = self._preprocess_contract(test_suite_path)
        collected_test_case_names = set(self._collect_test_case_names(preprocessed))

        # gather test cases that match any test case glob
        target_test_case_names: Set[str] = set()
        for test_case_name in collected_test_case_names:
            if len(test_cases_info.test_case_globs) == 0:
                target_test_case_names = collected_test_case_names
            else:
                for test_case_glob in test_cases_info.test_case_globs:
                    if fnmatch(test_case_name, test_case_glob):
                        target_test_case_names.add(test_case_name)

        # filter out test cases that match any test case glob
        not_ignored_target_test_case_names = (
            target_test_case_names.copy()
        )  # copy prevents changing lengths of this collection during loop execution
        for test_case_name in target_test_case_names:
            for ignored_test_case_glob in test_cases_info.ignored_test_case_globs:
                if fnmatch(test_case_name, ignored_test_case_glob):
                    not_ignored_target_test_case_names.remove(test_case_name)
                    break

        return TestSuite(
            test_path=test_suite_path,
            test_case_names=list(not_ignored_target_test_case_names),
            preprocessed_contract=preprocessed,
            setup_fn_name=self._find_setup_hook_name(preprocessed),
        )
