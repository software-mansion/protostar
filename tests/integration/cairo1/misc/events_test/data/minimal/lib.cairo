#[contract]
mod MinimalContract {
    #[event]
    fn Transfer() {}

    #[external]
    fn generate_event() {
        Transfer();
    }
}