import tempfile
import os
import pytest
import shutil

from .cache import CacheUtil


@pytest.fixture
def test_wrapper():
    cache_dir = []
    yield cache_dir
    assert len(cache_dir) == 1
    shutil.rmtree(cache_dir[0])


def test_cache_simple(test_wrapper):
    cache_name = "test-cache-simple"
    cache_util = CacheUtil(tempfile.gettempdir())
    test_wrapper.append(cache_util._cache_path)
    cache_file_path = os.path.join(cache_util._cache_path, cache_name)

    obj = {"a": 1, "b": True, "c": 63464, "z": None}

    assert cache_util.obtain(cache_name) is None

    cache_util.persist(cache_name, obj)

    assert cache_util.obtain(cache_name) == obj
    assert os.path.exists(cache_file_path)

    os.remove(cache_file_path)

    assert not os.path.exists(cache_file_path)
    assert cache_util.obtain(cache_name) is None


def test_cache_override(test_wrapper):
    cache_name = "test-cache-override"
    cache_util = CacheUtil(tempfile.gettempdir())
    test_wrapper.append(cache_util._cache_path)
    cache_file_path = os.path.join(cache_util._cache_path, cache_name)

    obj = {"a": 1, "b": True}
    obj2 = {"a": 2}

    assert cache_util.obtain(cache_name) is None

    cache_util.persist(cache_name, obj)
    cache_util.persist(cache_name, obj2)

    assert cache_util.obtain(cache_name) == obj2

    cache_util.persist(cache_name, obj, True)

    assert cache_util.obtain(cache_name) == obj

    cache_util.persist(cache_name, obj2, False)

    assert cache_util.obtain(cache_name) == obj
