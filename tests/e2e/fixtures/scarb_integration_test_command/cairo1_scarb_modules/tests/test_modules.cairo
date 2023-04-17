use cairo1_scarb_modules::internal_mod_foo::foo::foo_func;
use cairo1_scarb_modules::internal_mod_bar::bar::bar_func;

#[test]
fn test_modules_as_dependencies() {
    assert(foo_func() == 2137, 'foo_func() == 2137');
    assert(bar_func() == 2137, 'foo_func() == 2137');
}
