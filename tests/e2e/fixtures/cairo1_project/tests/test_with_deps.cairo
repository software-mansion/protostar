use external_lib_foo::foo::foo;
use external_lib_bar::bar::bar;

#[test]
fn test_assert_true() {
    foo();
    bar();
    let x = 1;
}
