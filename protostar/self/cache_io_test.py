import os

from .cache_io import CacheIO


def test_cache_simple(tmp_path):
    cache_name = "test-cache-simple"
    cache_io = CacheIO(tmp_path)
    # pylint: disable=protected-access
    cache_file_path = cache_io._cache_path / (cache_name + cache_io._EXTENSION)

    obj = {"a": 1, "b": True, "c": 63464, "z": None}

    assert cache_io.read(cache_name) is None

    cache_io.write(cache_name, obj)

    assert cache_io.read(cache_name) == obj

    os.remove(cache_file_path)

    assert cache_io.read(cache_name) is None

    # pylint: disable=protected-access
    assert cache_io._gitignore_path.read_text(encoding="utf-8") == "*\n"


def test_cache_override(tmp_path):
    cache_name = "test-cache-override"
    cache_io = CacheIO(tmp_path)

    obj = {"a": 1, "b": True}
    obj2 = {"a": 2}

    assert cache_io.read(cache_name) is None

    cache_io.write(cache_name, obj)
    cache_io.write(cache_name, obj2)

    assert cache_io.read(cache_name) == obj2

    cache_io.write(cache_name, obj)

    assert cache_io.read(cache_name) == obj

    # pylint: disable=protected-access
    assert cache_io._gitignore_path.read_text(encoding="utf-8") == "*\n"
