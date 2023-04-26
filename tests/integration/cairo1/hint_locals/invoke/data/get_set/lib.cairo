#[contract]
mod StorageContract {
    struct Storage {
        a: felt252
    }
    #[external]
    fn set_a(a_: felt252) {
        a::write(a_);
    }

    #[view]
    fn get_a() -> felt252 {
        a::read()
    }
}
