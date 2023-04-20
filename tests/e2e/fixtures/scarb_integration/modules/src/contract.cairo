#[contract]
mod BarContract {
    use modules_project::internal_mod_bar::bar::bar_func;

    #[view]
    fn internal_bar_func_wrapper() -> felt252 {
        bar_func()
    }
}
