#[contract]
mod MinimalContractWithConstructor {
    struct Storage {
        name: felt252,
    }

    #[constructor]
    fn constructor(
        name_: felt252
    ) {
        name::write(name_);
    }

    #[external]
    fn get_name() -> felt252 {
        name::read()
    }
}
