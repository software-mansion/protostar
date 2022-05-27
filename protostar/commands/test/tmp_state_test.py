from protostar.commands.test.tmp_state import TmpState


def test_empty_state_is_valid():
    tmp_state = TmpState()

    assert tmp_state.validate() is True


def test_tmp_state_supports_integers():
    tmp_state = TmpState()

    tmp_state.number = 42

    assert tmp_state.validate() is True


def test_tmp_state_supports_strings():
    tmp_state = TmpState()

    tmp_state.string = ""

    assert tmp_state.validate() is True


def test_tmp_state_supports_bools():
    tmp_state = TmpState()

    tmp_state.bool = False

    assert tmp_state.validate() is True


def test_not_supporting_dicts():
    tmp_state = TmpState()

    tmp_state.number = {}

    assert tmp_state.validate() is False


def test_forking():
    tmp_state = TmpState()
    tmp_state.foo = "foo"

    new_state = tmp_state.fork()
    new_state.foo = "bar"

    assert tmp_state.foo == "foo"
    assert new_state.foo == "bar"
