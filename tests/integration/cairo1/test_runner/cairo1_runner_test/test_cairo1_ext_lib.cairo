#[test]
fn passing_test_using_foo(){
    assert(1 == 1, 'simple check');
    external_lib_foo::foo::foo();
}

