use foo_contract::foo::FooContract::foo_func;

#[test]
fn test_bar_func(){
    assert(foo_func() == 2137, 'foo_func() == 2137');
}
