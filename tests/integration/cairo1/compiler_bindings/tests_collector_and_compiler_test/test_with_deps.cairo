use external_lib_foo::foo::foo;
use external_lib_bar::bar::bar;

#[test]
fn test_assert_true() {
    assert(1 == 1, 'simple check');
    foo();
    bar();
}
