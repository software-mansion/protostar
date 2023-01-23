IDENTITY_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> (res: felt) {
    return (arg,);
}
"""

CONTRACT_WITH_CONSTRUCTOR = """\
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    initial_balance: felt
) {
    balance.write(initial_balance);
    return ();
}

"""

CONTRACT_WITH_UINT256_CONSTRUCTOR = """\
%lang starknet
from starkware.cairo.common.math import assert_nn
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.uint256 import Uint256, uint256_add

@storage_var
func balance() -> (res: Uint256) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    let (res) = balance.read();
    let sum: Uint256 = uint256_add(res, amount);
    balance.write(sum);
    return ();
}

@external
func set_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    balance.write(amount);
    return ();
}


@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: Uint256) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    balance.write(amount);
    return ();
}

"""

FORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> felt {
    return arg;
}
"""

UNFORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg


) -> felt {
    return arg;
}
"""

BROKEN_CONTRACT = "I LOVE CAIRO"


RUNTIME_ERROR_CONTRACT = """\
%lang starknet

@external
func fail() {
    assert 0 = 1;
    return ();
}
"""

EMPTY_TEST = """\
%lang starknet

@external
func test_nothing() {
    return ();
}
"""

UINT256_IDENTITY_CONTRACT = """\
%lang starknet
from starkware.cairo.common.uint256 import Uint256

@view
func identity(arg: Uint256) -> (res: Uint256) {
    return (arg,);
}
"""

CAIRO_BINDINGS_CONTRACT = """\
enum MyEnumShort { a: felt, b: felt }
enum MyEnumLong { a: felt, b: felt, c: felt }
enum MyEnumGeneric<S, T> { a: T, b: S, c: T }
fn main() -> felt {
    let es0 = MyEnumShort::a(10);
    match_short(es0);
    let es1 = MyEnumShort::b(11);
    match_short(es1);

    let el0 = MyEnumLong::a(20);
    match_long(el0);
    let el1 = MyEnumLong::b(21);
    match_long(el1);
    let el2 = MyEnumLong::c(22);
    match_long(el2);
    let eg1: MyEnumGeneric::<(), felt> = MyEnumGeneric::<(), felt>::a(30);
    let eg2: MyEnumGeneric::<(), felt> = MyEnumGeneric::<(), felt>::b(());
    let eg3: MyEnumGeneric::<(), felt> = MyEnumGeneric::<(), felt>::c(32);
    300
}

fn match_short(e: MyEnumShort) -> felt {
    match e {
        MyEnumShort::a(x) => {
            x
        },
        MyEnumShort::b(x) => {
            x
        },
    }
}

fn match_long(e: MyEnumLong) -> felt {
    match e {
        MyEnumLong::a(x) => {
            x
        },
        MyEnumLong::b(x) => {
            x
        },
        MyEnumLong::c(x) => {
            x
        },
    }
}
"""
