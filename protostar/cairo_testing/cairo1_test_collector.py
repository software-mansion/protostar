from pathlib import Path
from typing import List, Iterable

import protostar.cairo.cairo_bindings as cairo1
from protostar.testing import TestCollector
from protostar.testing.test_collector import TestSuiteInfo
from protostar.testing.test_suite import Cairo1TestSuite, TestSuite, TestCase


class Cairo1TestCollectionException(Exception):
    pass


class Cairo1TestCollector(TestCollector):
    def __init__(self, cairo_path: list[str]):
        super().__init__(
            get_suite_function_names=self.collect_cairo1_tests_and_cache_outputs
        )
        self._cairo_path = cairo_path
        self._cairo_1_test_path_to_sierra_output: dict[Path, str] = {}

    def collect_cairo1_tests_and_cache_outputs(
        self,
        file_path: Path,
    ) -> List[str]:
        collector_output = cairo1.collect_tests(
            file_path,
            output_path=None,
            cairo_path=[Path(cp) for cp in self._cairo_path],
        )
        if not collector_output.sierra_output:
            raise Cairo1TestCollectionException(
                f"Compiler did not emit sierra output for {file_path}"
            )

        self._cairo_1_test_path_to_sierra_output[
            file_path
        ] = collector_output.sierra_output
        return collector_output.test_names

    def _build_test_suite_from_test_suite_info(
        self, test_suite_info: TestSuiteInfo
    ) -> TestSuite:
        test_suite = super()._build_test_suite_from_test_suite_info(test_suite_info)
        test_suite_sierra_output = self._cairo_1_test_path_to_sierra_output.get(
            test_suite.test_path
        )
        if not test_suite_sierra_output:
            raise Cairo1TestCollectionException(
                f"No sierra output found for {test_suite.test_path}"
            )

        return Cairo1TestSuite.from_test_suite(
            test_suite,
            sierra_output=test_suite_sierra_output,
        )

    def _collect_test_cases(
        self,
        function_names: List[str],
        test_path: Path,
    ) -> Iterable[TestCase]:
        setup_prefix = "setup_"

        fn_names = set(function_names)
        for test_fn_name in fn_names:
            setup_fn_name = setup_prefix + test_fn_name
            if setup_fn_name not in fn_names:
                setup_fn_name = None

            yield TestCase(
                test_path=test_path,
                test_fn_name=test_fn_name,
                setup_fn_name=setup_fn_name,
            )
