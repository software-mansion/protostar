#[contract]
mod ContractWithCtorPanicking {
    #[constructor]
    fn constructor(a: felt252, b: felt252) {
        assert(1 == 2, 'panic');
    }
    #[external]
    fn empty() {}
}
