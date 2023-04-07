use src::internal_mod_foo::foo::foo_func;
use src::internal_mod_bar::bar::bar_func;

#[test]
fn test_internal_dependencies() {
    assert(foo_func() == 2137, 'foo_func() == 2137');
    assert(bar_func() == 2137, 'foo_func() == 2137');
}
