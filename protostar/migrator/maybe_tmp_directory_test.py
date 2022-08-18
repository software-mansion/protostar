from pathlib import Path

from .maybe_tmp_directory import MaybeTmpDirectory


def test_directory_exists_when_if_not_empty(tmp_path: Path):
    output_dir = tmp_path / "tmp_dir"

    with MaybeTmpDirectory(output_dir):
        _save_some_file(output_dir / "some_file.txt")

    assert output_dir.exists()


def _save_some_file(file_path: Path):
    with open(file_path, "w", encoding="utf-8") as some_file:
        some_file.write("")


def test_directory_not_exists_if_empty(tmp_path: Path):
    output_dir = tmp_path / "tmp_dir"

    with MaybeTmpDirectory(output_dir):
        pass

    assert not output_dir.exists()
