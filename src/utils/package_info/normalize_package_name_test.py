from src.utils.package_info.normalize_package_name import normalize_package_name


def test_valid_name():
    assert normalize_package_name("foobar") == "foobar"


def test_name_with_dot():
    assert normalize_package_name("foo.py") == "foo_py"


def test_name_with_dash():
    assert normalize_package_name("foo-bar") == "foo_bar"
