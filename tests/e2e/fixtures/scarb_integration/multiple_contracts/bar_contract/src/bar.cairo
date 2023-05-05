#[contract]
mod BarContract {
    use foo_contract::foo::FooContract::foo_func;

    #[view]
    fn bar_func() -> felt252 {
        foo_func()
    }
}
