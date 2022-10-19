%lang starknet

from starkware.cairo.common.uint256 import Uint256, uint256_le

@external
func test_uint256_fail{range_check_ptr}(a: Uint256) {
    alloc_locals;
    let b: Uint256 = Uint256(0, 1);
    let condition: felt = uint256_le(b, a);
    if (condition == 1) {
        assert 1 = 0;
    }
    return ();
}