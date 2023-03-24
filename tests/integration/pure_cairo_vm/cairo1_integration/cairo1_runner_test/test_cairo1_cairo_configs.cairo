use array::ArrayTrait;

#[test]
#[available_gas(1000001)]
fn test_with_available_gas(){
    assert(1 == 1, 'simple check');
}

#[test]
#[should_panic]
fn test_with_should_panic(){
    assert(1 == 1, 'simple check');
}


