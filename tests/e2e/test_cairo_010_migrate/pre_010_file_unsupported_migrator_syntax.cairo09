%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func set_var{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }(val: felt):
    storage_felt.write(
        val # This is a comment which will crash auto-formatter
    )

    return ()
end
