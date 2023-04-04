#[contract]
mod MinimalContractWithConstructor {
    struct Storage {
        name: felt252,
    }

    #[derive(Drop, Copy)]
    struct Man {
        hunger: felt252,
        strength: felt252,
    }

    #[constructor]
    fn constructor(
        name_: felt252, man_: Man,
    ) {
        assert(man_.hunger != 0, 'no hungry people plz');
        name::write(name_);
    }

    #[external]
    fn get_name() -> felt252 {
        name::read()
    }
}