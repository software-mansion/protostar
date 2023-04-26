use modules_project::internal_mod_foo::foo::foo_func;
use modules_project::internal_mod_bar::bar::bar_func;

#[test]
fn modules_as_dependencies() {
    assert(foo_func() == 2137, 'foo_func() == 2137');
    assert(bar_func() == 2137, 'foo_func() == 2137');
}
