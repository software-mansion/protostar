use array::ArrayTrait;

extern type Bitwise;
extern fn bitwise(a: u128, b: u128) -> (u128, u128, u128) implicits(Bitwise) nopanic;

fn use_bitwise() {
    bitwise(1_u128, 1_u128);
}

fn use_pedersen() -> felt {
    assert(1 == 1, 'simple check');
    pedersen(1, 2)
}

#[test]
fn test_indirect_use() {
    use_pedersen();
    use_bitwise();
    assert(1 == 1, 'simple check');
}

#[test]
fn test_direct_use() {
    pedersen(1, 2);
    bitwise(1_u128, 1_u128);
    assert(1 == 1, 'simple check');
}


#[test]
fn test_pedersen_panic() {
    pedersen(1, 2);
    assert(1 == 2, 'simple check');
}


