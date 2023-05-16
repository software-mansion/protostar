#[contract]
mod WithDataContract {
    #[event]
    fn Transfer(from: felt252, to: felt252) {}

    #[external]
    fn generate_event() {
        Transfer(123, 456);
    }
}