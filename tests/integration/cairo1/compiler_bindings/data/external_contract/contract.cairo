#[contract]
mod SampleContract {
    struct InnerStruct {
        a: felt252
    }

    struct Storage {
        b: felt252,
    }

    #[view]
    fn view_b() -> felt252 {
        b::read()
    }
}
