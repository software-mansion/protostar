use libraries_project::contract::BarContract::external_bar_func_wrapper;

#[test]
fn test_contract_with_libraries_as_dependencies() {
    assert(external_bar_func_wrapper() == 2137, 'external_bar_func_wrapper');
}
