from src.commands.install.utils import map_url_to_package_name


def test_base_case():
    result = map_url_to_package_name("https://github.com/software-mansion/protostar")

    assert result == "protostar"


def test_dashes():
    result = map_url_to_package_name(
        "https://github.com/software-mansion/protostar-test"
    )

    assert result == "protostar_test"
