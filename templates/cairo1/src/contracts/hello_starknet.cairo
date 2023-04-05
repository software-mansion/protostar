#[contract]
mod HelloStarknet {
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

    // Calls a function defined in outside module
    #[view]
    fn get_two() -> felt252 {
        my_project::business_logic::utils::returns_two()
    }
}
