use src::main::fib;

#[test]
fn test_fib() {
    let x = fib(0, 1, 3);
    assert(x == 2, 'fib(0, 1, 3)');
}
