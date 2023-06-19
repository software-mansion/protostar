#[contract]
mod Contract2 {
    struct Storage {
        balance: felt252,
    }

    // Increases the balance by the given amount.
    #[external]
    fn set_balance(amount: felt252) {
        balance::write(amount);
    }
}
