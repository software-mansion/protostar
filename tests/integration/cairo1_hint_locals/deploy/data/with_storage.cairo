#[contract]
mod MinimalContract {
    struct Storage {
        value: felt252
    }
    #[external]
    fn set_value(new_value: felt252) {
        value::write(new_value);
    }
    #[view]
    fn get_value() -> felt252 {
        value::read()
    }
}
