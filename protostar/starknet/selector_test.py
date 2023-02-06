from .selector import Selector


def test_comparison():
    assert Selector("A") == Selector("A")
    assert Selector("A") != Selector("B")
