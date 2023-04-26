use modules_project::contract::BarContract::internal_bar_func_wrapper;

#[test]
fn contract_with_modules_as_dependencies() {
    assert(internal_bar_func_wrapper() == 2137, 'internal_bar_func_wrapper');
}
