use external_lib_foo::foo::foo_func;
use external_lib_bar::bar::bar_func;

#[test]
fn libraries_as_dependencies() {
    assert(foo_func() == 2137, 'foo_func() == 2137');
    assert(bar_func() == 2137, 'bar_func() == 2137');
}
