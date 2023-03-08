use src::main::fib;

#[test]
fn test_fib() {
    let x = fib(0, 1, 13);
    assert(x == 233, 'fib(0, 1, 13) == 233');
}
