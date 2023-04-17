#[contract]
mod HelloStarknet {
    use cairo1_scarb_modules::internal_mod_bar::bar::bar_func;

    struct Storage {
        balance: felt252,
    }

    // Increases the balance by the given amount.
    #[external]
    fn increase_balance(amount: felt252) {
        balance::write(balance::read() + amount);
    }

    // Returns the current balance.
    #[view]
    fn get_balance() -> felt252 {
        balance::read()
    }

    #[view]
    fn external_bar_func_wrapper() -> felt252 {
        bar_func()
    }
}
