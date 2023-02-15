#[contract]
mod HelloStarknet {
    #[external]
    fn do_something(amount: felt) -> felt {
        external_lib_foo::foo::foo();
        amount * 2
    }
}
