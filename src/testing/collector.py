import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Pattern


from src.starknet_compilation import StarknetCompiler
from src.testing.utils import collect_subdirectories


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """
    test_path: Path
    test_functions: List[dict]


@dataclass
class TestCollector:
    sources_directory: str
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
                if file.endswith(".cairo") and file.startswith("test_")
            ]
            for test_file_name in test_files:
                test_file_path = Path(root, test_file_name)

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

    def _collect_test_functions(self, file_path: Path) -> List[str]:
        preprocessed = StarknetCompiler(
            include_paths=collect_subdirectories(self.sources_directory)
        ).preprocess_contract(file_path)
        return [
            fn
            for fn in preprocessed.abi
            if fn["type"] == "function" and fn["name"].startswith("test_")
        ]
