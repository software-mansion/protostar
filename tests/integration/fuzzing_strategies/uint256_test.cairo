%lang starknet

from starkware.cairo.common.uint256 import Uint256, uint256_le

@external
func setup_uint256{range_check_ptr}() {
    %{
        max_examples(3)
        given(a=strategy.uint256(min_value=2))
    %}
    return ();
}

@external
func test_uint256{range_check_ptr}(a: Uint256) {
    tempvar b: Uint256 = Uint256(1, 0);
    let condition: felt = uint256_le(b, a);
    assert condition = 1;
    return ();
}

@external
func setup_uint256_mapping{range_check_ptr}() {
    %{
        max_examples(3)
        given(a=strategy.uint256().filter(lambda x: x.low > 100).map(lambda x: (x.low, 0) ))
    %}
    return ();
}

@external
func test_uint256_mapping{range_check_ptr}(a: Uint256) {
    tempvar b: Uint256 = Uint256(0, 1);
    tempvar c: Uint256 = Uint256(100, 0);
    %{
        print("---")
        print(reflect.a.get())
        print(reflect.b.get())
        print(reflect.c.get())
        print("---")
    %}
    let condition: felt = uint256_le(a, b);
    let condition2: felt = uint256_le(c, a);
    assert condition = 1;
    assert condition2 = 1;
    return ();
}