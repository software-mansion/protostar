#[contract]
mod HelloStarknet {
    #[external]
    fn do_something(amount: felt252) -> felt252 {
        external_lib_bar::bar::bar();
        amount * 2
    }
}
