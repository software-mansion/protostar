#[contract]
mod CalculateContract {
    #[view]
    fn calculate1(x: felt) -> felt {
        x + x * x
    }
    #[view]
    fn calculate2(x: felt) -> felt {
        (x + 1) * x - (x - 1)
    }
}
