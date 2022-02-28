import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Pattern

from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)

from src.utils.starknet_compilation import StarknetCompiler
from src.commands.test.reporter import TestReporter
from src.commands.test.utils import TestSubject


class CollectionError(Exception):
    pass


@dataclass
class TestCollector:
    sources_directory: Path
    include_paths: Optional[List[str]] = None

    # TODO: Optimize, by returning preprocessed test program, for reuse when compiling it for test runs
    def collect(
        self,
        match_pattern: Optional[Pattern] = None,
        omit_pattern: Optional[Pattern] = None,
    ) -> List[TestSubject]:
        test_sources = []
        for root, _, files in os.walk(self.sources_directory):
            test_files = [
                file
                for file in files
                if file.endswith(".cairo")
                and (file.startswith("test_") or file.endswith("_test.cairo"))
            ]
            for test_file_name in test_files:
                test_file_path = Path(root, test_file_name)
                test_file_path = test_file_path.resolve()

                if match_pattern and not match_pattern.match(str(test_file_path)):
                    continue
                if omit_pattern and omit_pattern.match(str(test_file_path)):
                    continue

                test_functions = self._collect_test_functions(test_file_path)
                if not test_functions:
                    continue

                test_sources.append(
                    TestSubject(
                        test_path=test_file_path,
                        test_functions=test_functions,
                    )
                )
        return test_sources

    def _collect_test_functions(self, file_path: Path) -> List[dict]:
        try:
            preprocessed = StarknetCompiler(
                include_paths=self.include_paths or [],
                disable_hint_validation=True,
            ).preprocess_contract(file_path)
        except PreprocessorError as p_err:
            TestReporter.report_collection_error()
            raise CollectionError from p_err
        return [
            fn
            for fn in preprocessed.abi
            if fn["type"] == "function" and fn["name"].startswith("test_")
        ]
