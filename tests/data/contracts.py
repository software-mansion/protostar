IDENTITY_CONTRACT = """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """

CONTRACT_WITH_CONSTRUCTOR = """\
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res : felt):
end

@external
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        amount : felt):
    let (res) = balance.read()
    balance.write(res + amount)
    return ()
end

@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        res : felt):
    let (res) = balance.read()
    return (res)
end

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        initial_balance : felt):
    balance.write(initial_balance)
    return ()
end
"""

FORMATTED_CONTRACT = """%lang starknet

@view
func identity(arg) -> (res : felt):
    return (arg)
end
"""

UNFORMATTED_CONTRACT = """%lang starknet

@view
func identity(arg


) -> (res : felt):
    return (arg)
end
"""

BROKEN_CONTRACT = "I LOVE CAIRO"

DATA_TRANSFORMER_UINT256_CONTRACT = """%lang starknet
from starkware.cairo.common.uint256 import Uint256
    
@external
func input_uint256(arg: Uint256):
    return ()
end
"""

DATA_TRANSFORMER_FELT_CONSTRUCTOR_CONTRACT = """%lang starknet

@constructor
func constructor(arg: felt):
    return ()
end
"""

DATA_TRANSFORMER_STRUCTS_CONTRACT = """%lang starknet

struct InnerStruct:
    member a: felt
    member b: felt
    member c: felt
end

struct OuterStruct:
    member felt_field: felt
    member inner_field: InnerStruct
end

@external
func input_outer_struct(arg: OuterStruct):
    return ()
end
"""

DATA_TRANSFORMER_LISTS_CONTRACT = """%lang starknet
from starkware.cairo.common.uint256 import Uint256

@external
func input_lists(
        felt_list_len: felt,
        felt_list: felt*,
        uint256_list_len: felt,
        uint256_list: Uint256*,
    ):
    return ()
end
"""

DATA_TRANSFORMER_TUPLE_CONTRACT = """%lang starknet

@external
func input_tuple(arg: (felt, felt)):
    return ()
end
"""

DATA_TRANSFORMER_OUTPUT_FELT_CONTRACT = """%lang starknet

@external
func output_felt() -> (res: felt):
    return (42)
end
"""

DATA_TRANSFORMER_EVENT_CONTRACT = """%lang starknet

@event
func event1(arg1: felt, arg2: felt):
end
"""
