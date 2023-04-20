from tests.e2e.conftest import CopyFixture, ProtostarFixture
from .conftest import execute_test


def test_pure_cairo_with_libraries_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_test(
        "libraries",
        "test_libraries_as_dependencies",
        "tests/test_pure_cairo.cairo",
        protostar,
        copy_fixture,
    )


def test_pure_cairo_with_modules_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_test(
        "modules",
        "test_modules_as_dependencies",
        "tests/test_pure_cairo.cairo",
        protostar,
        copy_fixture,
    )


# TODO #1767: investigate differences in gas support between quaireaux and protostar
# def test_pure_cairo_with_online_dependencies_using_scarb(
#     protostar: ProtostarFixture, copy_fixture: CopyFixture
# ):
#     execute_test(
#         "online_dependencies",
#         "test_online_repository_as_dependency",
#         "tests/test_pure_cairo.cairo",
#         protostar,
#         copy_fixture,
#     )
