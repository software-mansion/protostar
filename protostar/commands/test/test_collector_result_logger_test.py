from pathlib import Path
from typing import cast

from pytest_mock import MockerFixture

from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_collector_result_logger import (
    TestCollectorResultLogger,
)
from protostar.commands.test.test_suite import TestSuite


def test_logging_collected_one_test_suite_and_one_test_case(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollectorResultLogger(
        logger=logger_mock, test_result_formatter=mocker.MagicMock()
    ).log(
        TestCollector.Result(
            test_suites=[
                TestSuite(
                    test_case_names=["foo"],
                    test_path=Path(),
                )
            ],
        )
    )

    cast(mocker.MagicMock, logger_mock.info).call_args_list[0][0][0].startswith(
        "Collected 1 suite, and 1 test case"
    )


def test_logging_many_test_suites_and_many_test_cases(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollectorResultLogger(
        logger=logger_mock, test_result_formatter=mocker.MagicMock()
    ).log(
        TestCollector.Result(
            test_suites=[
                TestSuite(
                    test_case_names=["foo"],
                    test_path=Path(),
                ),
                TestSuite(
                    test_case_names=["foo"],
                    test_path=Path(),
                ),
            ],
        )
    )

    cast(mocker.MagicMock, logger_mock.info).call_args_list[0][0][0].startswith(
        "Collected 2 suites, and 2 test cases"
    )


def test_logging_no_cases_found(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollectorResultLogger(
        logger=logger_mock, test_result_formatter=mocker.MagicMock()
    ).log(test_collector_result=TestCollector.Result(test_suites=[]))

    cast(mocker.MagicMock, logger_mock.warning).assert_called_once_with(
        "No test cases found"
    )
