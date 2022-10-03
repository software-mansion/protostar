TEST_PARTIALLY_PASSING = """\
%lang starknet

@external
func test_pass1{syscall_ptr: felt*, range_check_ptr}() {
    assert 1 = 1;
    return ();
}

@external
func test_pass2{syscall_ptr: felt*, range_check_ptr}() {
    %{ assert 1 == 1 %}
    return ();
}

@external
func test_fail1{syscall_ptr: felt*, range_check_ptr}() {
    assert 1 = 2;
    return ();
}

@external
func test_fail2{syscall_ptr: felt*, range_check_ptr}() {
    %{ assert 1 == 2 %}
    return ();
}

"""

TEST_FAILING = """\
%lang starknet

@external
func test_fail1{syscall_ptr: felt*, range_check_ptr}() {
    assert 1 = 2;
    return ();
}

@external
func test_fail2{syscall_ptr: felt*, range_check_ptr}() {
    %{ assert 1 == 2 %}
    return ();
}
"""

TEST_PASSING = """\
%lang starknet

@external
func test_pass1{syscall_ptr: felt*, range_check_ptr}() {
    assert 1 = 1;
    return ();
}

@external
func test_pass2{syscall_ptr: felt*, range_check_ptr}() {
    %{ assert 1 == 1 %}
    return ();
}

"""

TEST_BROKEN = """\
%lang starknet

@external
func test_broken{syscall_ptr: felt*, range_check_ptr}() {
    %{ declare(1) %}
    return ();
}

"""
