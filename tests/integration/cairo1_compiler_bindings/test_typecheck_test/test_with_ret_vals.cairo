#[test]
fn test_ret_vals() ->  (felt252, felt252) {
    assert(1 == 1, 'simple check');
    return (6, 6);
}
