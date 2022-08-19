# pylint: disable=no-self-use

import re
from collections import defaultdict
from dataclasses import dataclass
from fnmatch import fnmatch
from glob import glob
from pathlib import Path
from time import time
from typing import Dict, List, Optional, Set, Tuple, Union, Iterable

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    LocationError,
    PreprocessorError,
)
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)

from protostar.commands.test.test_results import BrokenTestSuiteResult
from protostar.commands.test.test_suite import TestSuite, TestCase
from protostar.utils.compiler.pass_managers import TestCollectorPreprocessedProgram
from protostar.utils.starknet_compilation import StarknetCompiler

TestSuiteGlob = str
TestSuitePath = Path
TestCaseGlob = str
Target = str
"""e.g. `tests/**/::test_*`"""
TestCaseGlobsDict = Dict[TestSuitePath, Set[TestCaseGlob]]


@dataclass(frozen=True)
class ParsedTarget:
    test_suite_glob: TestSuiteGlob
    test_case_glob: TestCaseGlob

    @classmethod
    def from_target(
        cls, target: Target, default_test_suite_glob: Optional[TestSuiteGlob]
    ):
        test_suite_glob: Optional[TestSuiteGlob] = target
        test_case_glob: Optional[TestCaseGlob] = None
        if "::" in target:
            (test_suite_glob, test_case_glob) = target.split("::")
        test_suite_glob = test_suite_glob or default_test_suite_glob or "."

        if not test_case_glob:
            test_case_glob = "*"

        return cls(test_suite_glob, test_case_glob)


@dataclass
class TestSuiteInfo:
    path: Path
    test_case_globs: Set[TestCaseGlob]
    ignored_test_case_globs: Set[TestCaseGlob]

    def filter_test_cases(self, test_cases: Iterable[TestCase]) -> Iterable[TestCase]:
        for test_case in test_cases:
            if self.is_test_case_included(test_case):
                yield test_case

    def is_test_case_included(self, test_case: TestCase) -> bool:
        name = test_case.test_fn_name
        return fnmatch_any(name, self.test_case_globs) and (
            not fnmatch_any(name, self.ignored_test_case_globs)
        )


def fnmatch_any(name: str, pats: Iterable[str]) -> bool:
    for pat in pats:
        if fnmatch(name, pat):
            return True

    return False


TestSuiteInfoDict = Dict[TestSuitePath, TestSuiteInfo]


class TestCollector:
    @dataclass
    class Config:
        safe_collecting: bool = False

    class Result:
        def __init__(
            self,
            test_suites: List[TestSuite],
            broken_test_suites: Optional[List[BrokenTestSuiteResult]] = None,
            duration: float = 0.0,
        ) -> None:
            self.test_suites = test_suites
            self.broken_test_suites: List[BrokenTestSuiteResult] = (
                broken_test_suites or []
            )
            self.test_cases_count = sum(
                [len(test_suite.test_cases) for test_suite in test_suites]
            )
            self.duration = duration

    def __init__(
        self, starknet_compiler: StarknetCompiler, config: Optional[Config] = None
    ) -> None:
        self._starknet_compiler = starknet_compiler
        self._config = config or TestCollector.Config()

    supported_test_suite_filename_patterns = [
        re.compile(r"^test_.*\.cairo"),
        re.compile(r"^.*_test\.cairo"),
    ]

    @classmethod
    def is_test_suite(cls, filename: str) -> bool:
        return any(
            test_re.match(filename)
            for test_re in cls.supported_test_suite_filename_patterns
        )

    def collect(
        self,
        targets: List[Target],
        ignored_targets: Optional[List[Target]] = None,
        default_test_suite_glob: Optional[str] = None,
    ) -> "TestCollector.Result":
        start_time = time()

        parsed_targets = self.parse_targets(set(targets), default_test_suite_glob)
        ignored_parsed_targets = self.parse_targets(
            set(ignored_targets or []), default_test_suite_glob
        )

        test_case_globs_dict = self.build_test_case_globs_dict(parsed_targets)
        ignored_test_case_globs_dict = self.build_test_case_globs_dict(
            ignored_parsed_targets
        )

        filtered_test_case_globs_dict = self.filter_out_ignored_test_suites(
            test_case_globs_dict,
            ignored_test_case_globs_dict,
        )

        test_suite_info_dict = self.build_test_suite_info_dict(
            filtered_test_case_globs_dict,
            ignored_test_case_globs_dict,
        )

        (
            test_suites,
            broken_test_suites,
        ) = self._build_test_suites_from_test_suite_info_dict(test_suite_info_dict)

        non_empty_test_suites = [
            test_suite for test_suite in test_suites if test_suite.test_cases
        ]

        end_time = time()

        return TestCollector.Result(
            non_empty_test_suites,
            broken_test_suites=broken_test_suites,
            duration=end_time - start_time,
        )

    def build_test_case_globs_dict(
        self,
        parsed_targets: Set[ParsedTarget],
    ) -> TestCaseGlobsDict:
        results: TestCaseGlobsDict = defaultdict(set)

        for parsed_target in parsed_targets:
            test_suite_paths = self._find_test_suite_paths_from_glob(
                parsed_target.test_suite_glob
            )
            for test_suite_path in test_suite_paths:
                results[test_suite_path].add(parsed_target.test_case_glob)
        return results

    def parse_targets(
        self, targets: Set[Target], default_test_suite_glob: Optional[str] = None
    ) -> Set[ParsedTarget]:
        return {
            ParsedTarget.from_target(target, default_test_suite_glob)
            for target in targets
        }

    def filter_out_ignored_test_suites(
        self,
        test_case_globs_dict: TestCaseGlobsDict,
        ignored_test_case_globs_dict: TestCaseGlobsDict,
    ) -> TestCaseGlobsDict:
        result = test_case_globs_dict.copy()

        for ignored_target_path in ignored_test_case_globs_dict:
            if (
                "*" in ignored_test_case_globs_dict[ignored_target_path]
                and ignored_target_path in result
            ):
                del result[ignored_target_path]
        return result

    def build_test_suite_info_dict(
        self,
        test_case_globs_dict: TestCaseGlobsDict,
        ignored_test_case_globs_dict: TestCaseGlobsDict,
    ) -> TestSuiteInfoDict:
        result: TestSuiteInfoDict = {}
        for test_suite_path in test_case_globs_dict:
            test_suite_info = result.setdefault(
                test_suite_path,
                TestSuiteInfo(
                    test_case_globs=set(),
                    ignored_test_case_globs=set(),
                    path=test_suite_path,
                ),
            )
            test_suite_info.test_case_globs = test_case_globs_dict[test_suite_path]
            if test_suite_path in ignored_test_case_globs_dict:
                test_suite_info.ignored_test_case_globs = ignored_test_case_globs_dict[
                    test_suite_path
                ]
        return result

    def _find_test_suite_paths_from_glob(
        self, test_suite_glob: str
    ) -> Set[TestSuitePath]:
        results: Set[Path] = set()
        matches = glob(test_suite_glob, recursive=True)
        for match in matches:
            path = Path(match)
            if path.is_dir():
                results.update(self._find_test_suite_paths_in_dir(path))
            elif path.is_file() and TestCollector.is_test_suite(path.name):
                results.add(path)
        return results

    def _find_test_suite_paths_in_dir(self, path: Path) -> Set[TestSuitePath]:
        filepaths = set(glob(f"{path}/**/*.cairo", recursive=True))
        results: Set[Path] = set()
        for filepath in filepaths:
            path = Path(filepath)
            if TestCollector.is_test_suite(path.name):
                results.add(path)
        return results

    def _build_test_suites_from_test_suite_info_dict(
        self,
        test_suite_info_dict: TestSuiteInfoDict,
    ) -> Tuple[List[TestSuite], List[BrokenTestSuiteResult]]:
        test_suites: List[TestSuite] = []
        broken_test_suites: List[BrokenTestSuiteResult] = []

        for test_suite_info in test_suite_info_dict.values():
            try:
                test_suites.append(
                    self._build_test_suite_from_test_suite_info(
                        test_suite_info,
                    )
                )
            except (PreprocessorError, LocationError) as err:
                broken_test_suites.append(
                    BrokenTestSuiteResult(
                        file_path=test_suite_info.path,
                        test_case_names=[],
                        exception=err,
                    )
                )

        return test_suites, broken_test_suites

    def _build_test_suite_from_test_suite_info(
        self,
        test_suite_info: TestSuiteInfo,
    ) -> TestSuite:
        preprocessed = self._starknet_compiler.preprocess_contract(test_suite_info.path)
        setup_fn_name = self._collect_setup_hook_name(preprocessed)

        test_cases = list(
            test_suite_info.filter_test_cases(self._collect_test_cases(preprocessed))
        )

        return TestSuite(
            test_path=test_suite_info.path,
            test_cases=test_cases,
            setup_fn_name=setup_fn_name,
        )

    def _collect_test_cases(
        self,
        preprocessed: Union[
            StarknetPreprocessedProgram, TestCollectorPreprocessedProgram
        ],
    ) -> Iterable[TestCase]:
        for fn_name in self._starknet_compiler.get_function_names(preprocessed):
            if fn_name.startswith("test_"):
                yield TestCase(test_fn_name=fn_name)

    def _collect_setup_hook_name(
        self,
        preprocessed: Union[
            StarknetPreprocessedProgram, TestCollectorPreprocessedProgram
        ],
    ) -> Optional[str]:
        hook_name = "__setup__"
        function_names = self._starknet_compiler.get_function_names(preprocessed)

        if function_names.count(hook_name) == 1:
            return hook_name
        return None
