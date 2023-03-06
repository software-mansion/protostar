#[contract]
mod BalanceContract {
    struct Storage {
        balance: felt
    }

    #[external]
    fn increase_balance(amount: felt) {
        balance::write(balance::read() + amount);
    }

    #[view]
    fn get_balance() -> felt {
        balance::read()
    }

    #[constructor]
    fn constructor() {
        balance::write(0);
    }
}
