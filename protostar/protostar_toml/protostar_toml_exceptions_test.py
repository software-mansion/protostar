from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)


def test_message_includes_section_name():
    ex = InvalidProtostarTOMLException("SECTION")

    assert "SECTION" in str(ex)


def test_message_includes_section_and_attribute_names():
    ex = InvalidProtostarTOMLException("SECTION", "ATTRIBUTE")

    assert "SECTION" in str(ex)
    assert "ATTRIBUTE" in str(ex)
