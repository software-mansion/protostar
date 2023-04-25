#[contract]
mod FibContract {
    use quaireaux_math::fibonacci;

    #[view]
    fn fib_wrapper(a: felt252, b: felt252, n: felt252) -> felt252 {
        fibonacci::fib(a, b, n)
    }
}
