%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.hash import hash2

@view
func hash_magic_numbers{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*}():
    hash2{hash_ptr=pedersen_ptr}(21, 37)

    return ()
end
