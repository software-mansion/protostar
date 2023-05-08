#[contract]
mod HelloStarknet {
    #[external]
    fn do_something(amount: felt252) -> felt252 {
        external_lib_foo::foo::foo();
        amount * 2
    }
}
