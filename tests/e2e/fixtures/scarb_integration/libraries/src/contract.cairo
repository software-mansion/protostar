#[contract]
mod BarContract {
    use external_lib_bar::bar::bar_func;

    #[view]
    fn external_bar_func_wrapper() -> felt252 {
        bar_func()
    }
}
