use example_package::fib;

#[test]
fn test_my_test() {
    assert(fib(0, 1, 10) == 55, fib(0, 1, 10));
    assert(2 == 2, 'aa');
}

#[test]
fn test_four() {
    assert(4 == 4, '4 == 4');
}