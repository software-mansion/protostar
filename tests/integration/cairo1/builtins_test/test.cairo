use array::ArrayTrait;

fn test_pedersen() -> felt {
    //assert(1 == 1, 'simple check');
    pedersen(1, 2)
}

#[test]
fn test_ok() {
    test_pedersen();
    assert(1 == 1, 'simple check');
}

#[test]
fn test_ok2() {
    pedersen(1, 2);
    assert(1 == 1, 'simple check');
}


#[test]
fn test_pedersen_panic() {
    pedersen(1, 2);
    assert(1 == 2, 'simple check');
}

