#[test]
fn test_ret_vals() ->  (felt, felt) {
    assert(1 == 1, 'simple check');
    return (6, 6);
}
