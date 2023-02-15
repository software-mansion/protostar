#[contract]
mod HelloStarknet {
    #[external]
    fn do_something(amount: felt) -> felt {
        external_lib_bar::bar::bar();
        amount * 2
    }
}
