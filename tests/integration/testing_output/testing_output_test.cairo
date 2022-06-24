%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.hash import hash2

@external
func test_printing_builtin_usage{pedersen_ptr : HashBuiltin*}():
    hash2{hash_ptr=pedersen_ptr}(21, 37)

    # assert in the pytest file
    return ()
end
