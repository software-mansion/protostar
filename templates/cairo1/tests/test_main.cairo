#[test]
#[available_gas(10000)]
fn test_get_available_gas_with_gas_supply() {
    assert(testing::get_available_gas() > 1000_u128, 'too much gas used')
}
