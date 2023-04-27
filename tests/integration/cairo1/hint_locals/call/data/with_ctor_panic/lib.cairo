use array::ArrayTrait;

#[contract]
mod ContractWithCtorPanicking {
    use array::ArrayTrait;

    #[constructor]
    fn constructor(a: felt252, b: felt252) {
        let mut panic_data = ArrayTrait::new();
        panic_data.append('panic from ctor');

        panic(panic_data);
    }

    #[external]
    fn empty() {}
}
