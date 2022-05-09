import os
import re
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Generator, List, Optional, Pattern, cast

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)

from src.commands.test.test_subject_queue import TestSubject
from src.protostar_exception import ProtostarException
from src.utils.starknet_compilation import StarknetCompiler


class CollectionError(ProtostarException):
    pass


@dataclass
class TestCollector:
    @dataclass(frozen=True)
    class Result:
        test_subjects: List[TestSubject]
        test_cases_count: int

        def log(self, logger: Logger):
            if self.test_cases_count:
                result: List[str] = ["Collected"]
                suits_count = len(self.test_subjects)
                if suits_count == 1:
                    result.append("1 suit,")
                else:
                    result.append(f"{suits_count} suits,")

                result.append("and")
                if self.test_cases_count == 1:
                    result.append("1 test case")
                else:
                    result.append(f"{self.test_cases_count} test cases")

                logger.info(" ".join(result))
            else:
                logger.warn("No cases found")

    target: Path
    include_paths: Optional[List[str]] = None
    target_function: Optional[str] = None
    test_filename_re = [re.compile(r"^test_.*\.cairo"), re.compile(r"^.*_test.cairo")]

    def __post_init__(self):
        if re.match(r"^.*\.cairo::.*", self.target.name):
            file_name, self.target_function = self.target.name.split("::")
            self.target = self.target.parent / file_name
            assert not self.target.is_dir()

    def collect(
        self,
        match_pattern: Optional[Pattern] = None,
        omit_pattern: Optional[Pattern] = None,
    ) -> "TestCollector.Result":

        test_files = self._get_test_files()

        if match_pattern:
            test_files = filter(
                lambda file: cast(Pattern, match_pattern).match(file.name), test_files
            )
        if omit_pattern:
            test_files = filter(
                lambda file: not cast(Pattern, omit_pattern).match(file.name),
                test_files,
            )

        test_files = map(self._build_test_subject, test_files)
        test_subjects = list(
            filter(lambda file: (file.test_functions) != [], test_files)
        )
        return TestCollector.Result(
            test_subjects=test_subjects,
            test_cases_count=sum(
                [len(subject.test_functions) for subject in test_subjects]
            ),
        )

    @classmethod
    def is_test_file(cls, filename: str) -> bool:
        return any(test_re.match(filename) for test_re in cls.test_filename_re)

    def _build_test_subject(self, file_path: Path):
        test_functions = self._collect_test_functions(file_path)
        if self.target_function:
            test_functions = [
                f for f in test_functions if f["name"] == self.target_function
            ]
        return TestSubject(
            test_path=file_path,
            test_functions=test_functions,
        )

    def _get_test_files(self) -> Generator[Path, None, None]:
        if not self.target.is_dir():
            yield self.target
            return
        for root, _, files in os.walk(self.target):
            test_files = [Path(root, file) for file in files]
            test_files = filter(lambda file: self.is_test_file(file.name), test_files)
            for test_file in test_files:
                yield test_file

    def _collect_test_functions(self, file_path: Path) -> List[dict]:
        try:
            preprocessed = StarknetCompiler(
                include_paths=self.include_paths or [],
                disable_hint_validation=True,
            ).preprocess_contract(file_path)
        except PreprocessorError as p_err:
            print(p_err)
            raise CollectionError("Failed to collect test cases") from p_err
        return [
            fn
            for fn in preprocessed.abi
            if fn["type"] == "function" and fn["name"].startswith("test_")
        ]
