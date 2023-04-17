#[contract]
mod CalculateContract {
    #[view]
    fn calculate1(x: felt252) -> felt252 {
        x + x * x
    }
    #[view]
    fn calculate2(x: felt252) -> felt252 {
        (x + 1) * x - (x - 1)
    }
}
