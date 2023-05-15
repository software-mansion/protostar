#[contract]
mod SimpleContract {
    #[event]
    fn Transfer() {}

    #[external]
    fn generate_event() {
        Transfer();
    }
}