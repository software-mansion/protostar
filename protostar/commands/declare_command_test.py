import pytest

from protostar.starknet_gateway import SuccessfulDeclareResponse, FakeBlockExplorer

from .declare_command import format_successful_declare_response


@pytest.mark.parametrize(
    "test_input",
    [
        SuccessfulDeclareResponse("", 123, 456),
        SuccessfulDeclareResponse("", 0, 0),
        SuccessfulDeclareResponse("", 123, 123),
    ],
)
def test_declare_response_formatting(test_input: SuccessfulDeclareResponse):
    formatted = format_successful_declare_response(
        test_input, FakeBlockExplorer()
    ).split("\n")
    assert formatted[0] == "Declare transaction was sent."

    class_hash = formatted[1][formatted[1].find(":") + 1 :].strip()
    transaction_hash = formatted[2][formatted[2].find(":") + 1 :].strip()

    assert class_hash == f"0x{test_input.class_hash:064x}"
    assert int(class_hash, 16) == test_input.class_hash

    assert transaction_hash == f"0x{test_input.transaction_hash:064x}"
    assert int(transaction_hash, 16) == test_input.transaction_hash
