from src.commands.install.utils import map_slug_to_package_name


def test_base_case():
    result = map_slug_to_package_name("software-mansion/protostar")

    assert result == "protostar"


def test_dashes():
    result = map_slug_to_package_name("software-mansion/protostar-test")

    assert result == "protostar_test"
