#[contract]
mod ContractWithCtor {
    #[constructor]
    fn constructor(a: felt252, b: felt252) {}
    #[external]
    fn empty() {}
}
