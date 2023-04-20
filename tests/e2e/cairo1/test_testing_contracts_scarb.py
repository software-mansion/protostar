from tests.e2e.conftest import CopyFixture, ProtostarFixture
from .conftest import execute_test


def test_contract_with_libraries_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_test(
        "libraries",
        "test_contract_with_libraries_as_dependencies",
        "tests/test_contract.cairo",
        protostar,
        copy_fixture,
    )


def test_contract_with_modules_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_test(
        "modules",
        "test_contract_with_modules_as_dependencies",
        "tests/test_contract.cairo",
        protostar,
        copy_fixture,
    )


# TODO #1767: investigate differences in gas support between quaireaux and protostar
# def test_contract_with_online_dependencies_using_scarb(
#     protostar: ProtostarFixture, copy_fixture: CopyFixture
# ):
#     execute_test(
#         "online_dependencies",
#         "test_contract_with_online_repository_as_dependency",
#         "tests/test_contract.cairo",
#         protostar,
#         copy_fixture,
#     )
