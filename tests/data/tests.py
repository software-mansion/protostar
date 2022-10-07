TEST_PARTIALLY_PASSING = """\
%lang starknet

@external
func test_pass1() {
    assert 1 = 1;
    return ();
}

@external
func test_pass2() {
    %{ assert 1 == 1 %}
    return ();
}

@external
func test_fail1() {
    assert 1 = 2;
    return ();
}

@external
func test_fail2() {
    %{ assert 1 == 2 %}
    return ();
}

"""

TEST_FAILING = """\
%lang starknet

@external
func test_fail1() {
    assert 1 = 2;
    return ();
}

@external
func test_fail2() {
    %{ assert 1 == 2 %}
    return ();
}
"""

TEST_PASSING = """\
%lang starknet

@external
func test_pass1() {
    assert 1 = 1;
    return ();
}

@external
func test_pass2() {
    %{ assert 1 == 1 %}
    return ();
}

"""

TEST_BROKEN = """\
%lang starknet

@external
func test_broken() {
    %{ declare(1) %}
    return ();
}

"""
