mod contract1;

#[contract]
mod MinimalContract {
    #[constructor]
    fn constructor() {
    }

    #[external]
    fn empty() {}
}
