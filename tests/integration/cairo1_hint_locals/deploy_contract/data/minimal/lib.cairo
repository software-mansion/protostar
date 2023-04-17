#[contract]
mod MinimalContract {
    #[external]
    fn empty() {}
    #[external]
    fn perform(a: felt252, b: felt252, c: felt252) -> felt252 {
        (a+b)*c
    }
}
