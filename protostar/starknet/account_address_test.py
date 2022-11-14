from .account_address import AccountAddress


def test_matches_snapshot():
    account_address = AccountAddress.from_class_hash(
        class_hash=0,
        salt=0,
        constructor_calldata=[],
    ).as_str()

    assert (
        account_address
        == "0x064820103001fcf57dc33ea01733a819529381f2df018c97621e4089f0f0d355"
    )
