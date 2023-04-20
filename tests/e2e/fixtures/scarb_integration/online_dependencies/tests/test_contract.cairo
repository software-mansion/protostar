use online_dependencies_project::contract::FibContract::fib_wrapper;

#[test]
fn contract_with_online_repository_as_dependency() {
    assert(fib_wrapper(0, 1, 10) == 55, 'fib_wrapper(0, 1, 10) == 55');
}
