import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.starknet_compilation import preprocess_contract


@dataclass
class TestSource:
    target_path: Path
    test_path: Path
    test_functions: List[dict]


@dataclass
class TestCollector:
    sources_directory: str

    # TODO: Optimize, by returning preprocessed test program, for reuse when compiling it for test runs
    def collect(self) -> List[TestSource]:
        test_sources = []
        for root, _, files in os.walk(self.sources_directory):
            test_files = [
                file
                for file in files
                if file.endswith(".cairo") and file.startswith("test_")
            ]
            for test_file_name in test_files:
                test_file_path = Path(root + test_file_name)

                # TODO: Allow relocating tests from source, requires pre-collection of cairo files
                target_contract_file_name = test_file_name.replace("_test", "")
                target_contract_file_path = Path(root + target_contract_file_name)

                if not target_contract_file_path.is_file():
                    continue

                test_functions = TestCollector._collect_test_functions(test_file_path)
                if not test_functions:
                    continue

                test_sources.append(
                    TestSource(
                        target_path=target_contract_file_path,
                        test_path=test_file_path,
                        test_functions=test_functions,
                    )
                )

        return test_sources

    @staticmethod
    def _collect_test_functions(file_path: Path) -> List[str]:
        preprocessed = preprocess_contract(file_path)
        return [
            fn
            for fn in preprocessed.abi
            if fn["type"] == "function" and fn["name"].startswith("test_")
        ]
