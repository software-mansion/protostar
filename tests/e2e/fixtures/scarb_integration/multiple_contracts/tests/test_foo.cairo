use bar_contract::bar::BarContract::bar_func;

#[test]
fn test_foo_func(){
    assert(bar_func() == 2137, 'bar_func() == 2137');
}
