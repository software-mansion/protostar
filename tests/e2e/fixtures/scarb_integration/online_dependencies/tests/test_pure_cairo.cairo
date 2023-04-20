use quaireaux_math::fibonacci;

#[test]
fn online_repository_as_dependency() {
    assert(fibonacci::fib(0, 1, 10) == 55, 'fibonacci::fib(0, 1, 10) == 55');
}
