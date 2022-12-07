from pathlib import Path

from protostar.configuration_file import FakeConfigurationFile

from .lib_path_resolver import LibPathResolver


def test_happy_case_in_legacy_mode(tmp_path: Path):
    resolver = LibPathResolver(
        project_root_path=tmp_path,
        configuration_file=FakeConfigurationFile(lib_path=tmp_path / "deps"),
        legacy_mode=True,
    )

    result = resolver.resolve(lib_path_provided_as_arg=None)

    assert result == tmp_path / "deps"


def test_default_value_in_legacy_mode(tmp_path: Path):
    resolver = LibPathResolver(
        project_root_path=tmp_path,
        configuration_file=FakeConfigurationFile(lib_path=None),
        legacy_mode=True,
    )

    result = resolver.resolve(lib_path_provided_as_arg=None)

    assert result == tmp_path / "lib"


def test_arg_is_provided_in_legacy_mode(
    tmp_path: Path,
):
    resolver = LibPathResolver(
        project_root_path=tmp_path,
        configuration_file=FakeConfigurationFile(lib_path=tmp_path / "deps"),
        legacy_mode=True,
    )

    result = resolver.resolve(lib_path_provided_as_arg=Path("deps2"))

    assert result == tmp_path / "deps"


def test_happy_case_when_legacy_mode_is_off(tmp_path: Path):
    resolver = LibPathResolver(
        project_root_path=tmp_path,
        configuration_file=FakeConfigurationFile(lib_path=tmp_path / "deps"),
        legacy_mode=False,
    )

    result = resolver.resolve(lib_path_provided_as_arg=Path("deps2"))

    assert result == tmp_path / "deps2"


def test_default_value_when_legacy_mode_is_off(tmp_path: Path):
    resolver = LibPathResolver(
        project_root_path=tmp_path,
        configuration_file=FakeConfigurationFile(lib_path=tmp_path / "deps"),
        legacy_mode=False,
    )

    result = resolver.resolve(lib_path_provided_as_arg=None)

    assert result == tmp_path / "lib"
