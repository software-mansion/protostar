from pathlib import Path

import pytest

from .configuration_strict_toml_interpreter import (
    ConfigurationStrictTOMLInterpreter,
    LazyFileReader,
)


class LazyFileReaderDouble(LazyFileReader):
    def __init__(self, content: str) -> None:
        self._content = content
        super().__init__(file_path=Path())

    def get_filename(self) -> str:
        return "lazy_file_reader_double_filename.toml"

    def get_file_content(self) -> str:
        return self._content


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture() -> str:
    return """\
    [ns.section]
    attr = "attr_val"

    ["quoted.section"]
    attr = "attr_val"

    [profile.profile_name_1]
    attr = "overwritten_attr_val"

    [profile.profile_name_2]
    attr = "overwritten_attr_val"
    """


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(tmp_path: Path, protostar_toml_content: str) -> Path:
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    return protostar_toml_path


@pytest.fixture(name="lazy_protostar_toml_reader")
def lazy_protostar_toml_reader_fixture(protostar_toml_content: str):
    return LazyFileReaderDouble(content=protostar_toml_content)


def test_getting_attribute(protostar_toml_path: Path):
    interpreter = ConfigurationStrictTOMLInterpreter(
        lazy_file_reader=LazyFileReader(file_path=protostar_toml_path),
    )

    result = interpreter.get_attribute(
        section_namespace="ns", section_name="section", attribute_name="attr"
    )

    assert result == "attr_val"


def test_getting_section(lazy_protostar_toml_reader):
    interpreter = ConfigurationStrictTOMLInterpreter(
        lazy_file_reader=lazy_protostar_toml_reader,
    )

    result = interpreter.get_section(section_namespace="ns", section_name="section")

    assert result is not None
    assert result["attr"] == "attr_val"


def test_not_getting_section_in_quotes(lazy_protostar_toml_reader):
    interpreter = ConfigurationStrictTOMLInterpreter(
        lazy_file_reader=lazy_protostar_toml_reader,
    )

    result = interpreter.get_section(section_namespace="quoted", section_name="section")

    assert result is None


def test_getting_profile_names(lazy_protostar_toml_reader):
    interpreter = ConfigurationStrictTOMLInterpreter(
        lazy_file_reader=lazy_protostar_toml_reader,
    )

    result = interpreter.get_profile_names()

    assert result == ["profile_name_1", "profile_name_2"]


def test_getting_filename(lazy_protostar_toml_reader):
    interpreter = ConfigurationStrictTOMLInterpreter(
        lazy_file_reader=lazy_protostar_toml_reader,
    )

    result = interpreter.get_filename()

    assert result == "lazy_file_reader_double_filename.toml"
