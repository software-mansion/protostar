import tempfile
import os
import shutil
from pathlib import Path

import pytest

from .cache_io import CacheIO


@pytest.fixture(name="test_wrapper")
def test_wrapper_fixture():
    cache_dir = []
    yield cache_dir
    assert len(cache_dir) == 1
    shutil.rmtree(cache_dir[0])


def test_cache_simple(test_wrapper):
    cache_name = "test-cache-simple"
    cache_io = CacheIO(Path(tempfile.gettempdir()))
    # pylint: disable=protected-access
    test_wrapper.append(cache_io._cache_path)
    # pylint: disable=protected-access
    cache_file_path = cache_io._cache_path / (cache_name + cache_io._EXTENSION)

    obj = {"a": 1, "b": True, "c": 63464, "z": None}

    assert cache_io.read(cache_name) is None

    cache_io.write(cache_name, obj)

    assert cache_io.read(cache_name) == obj

    os.remove(cache_file_path)

    assert not cache_file_path.exists()
    assert cache_io.read(cache_name) is None


def test_cache_override(test_wrapper):
    cache_name = "test-cache-override"
    cache_io = CacheIO(Path(tempfile.gettempdir()))
    # pylint: disable=protected-access
    test_wrapper.append(cache_io._cache_path)

    obj = {"a": 1, "b": True}
    obj2 = {"a": 2}

    assert cache_io.read(cache_name) is None

    cache_io.write(cache_name, obj)
    cache_io.write(cache_name, obj2)

    assert cache_io.read(cache_name) == obj2

    cache_io.write(cache_name, obj, True)

    assert cache_io.read(cache_name) == obj

    cache_io.write(cache_name, obj2, False)

    assert cache_io.read(cache_name) == obj
