DATA_TRANSFORMER_UINT256_CONTRACT = """%lang starknet
from starkware.cairo.common.uint256 import Uint256
    
@external
func input_uint256(arg: Uint256) {
    return ();
}
"""

DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT = """%lang starknet

@constructor
func constructor(arg: felt) {
    return ();
}
"""

DATA_TRANSFORMER_STRUCTS_CONTRACT = """%lang starknet

struct InnerStruct {
    a: felt,
    b: felt,
    c: felt,
}

struct OuterStruct {
    felt_field: felt,
    inner_field: InnerStruct,
}

@external
func input_outer_struct(arg: OuterStruct) {
    return ();
}
"""

DATA_TRANSFORMER_LISTS_CONTRACT = """%lang starknet
from starkware.cairo.common.uint256 import Uint256

@external
func input_lists(
        felt_list_len: felt,
        felt_list: felt*,
        uint256_list_len: felt,
        uint256_list: Uint256*,
    ) {
    return ();
}
"""

DATA_TRANSFORMER_TUPLE_CONTRACT = """%lang starknet

@external
func input_tuple(arg: (felt, felt)) {
    return ();
}
"""

DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT = """%lang starknet

@external
func output_felt() -> (res: felt) {
    return (42,);
}
"""

DATA_TRANSFORMER_EVENT_CONTRACT = """%lang starknet

@event
func event1(arg1: felt, arg2: felt) {
}
"""
