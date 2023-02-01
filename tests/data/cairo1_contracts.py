CAIRO_1_BASIC_STARKNET_CONTRACT = """\
#[contract]
mod HelloStarknet {
    struct Storage { balance: felt, }

    // Increases the balance by the given amount.
    #[external]
    fn increase_balance(amount: felt) {
        balance::write(balance::read() + amount);
    }

    // Returns the current balance.
    #[view]
    fn get_balance() -> felt {
        balance::read()
        0
    }
}
"""
CAIRO_1_BASIC_STARKNET_TEST = """\
#[abi]
trait IAnotherContract {
fn foo(); }


#[contract]
mod TestContract {
    struct Storage { my_storage_var: felt, }

    fn internal_func() -> felt {
        1
    }

    #[external]
    fn test(ref arg: felt, arg1: felt, arg2: felt) -> felt {
        let x = my_storage_var::read();
        my_storage_var::write(x + 1);
        x + internal_func()
    }

    #[external]
    fn empty() {
    }
}
"""
CAIRO_1_ENUM_CONTRACT = """\
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
CAIRO_ROLL_TEST = """\
#[test]
fn test_cheatcode_caller() {
   roll(1, 2)
}
#[test]
fn test_cheatcode_caller_twice() {
   roll(1, 2);
   roll(1, 2)
}
#[test]
fn test_cheatcode_caller_three() {
   roll(1, 2);
   roll(1, 2);
   roll(1, 2)
}
"""
