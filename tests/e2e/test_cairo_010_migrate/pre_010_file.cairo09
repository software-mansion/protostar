%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func storage_felt() -> (res: felt):
end

@external
func set_var{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }(val: felt):
    storage_felt.write(val)

    return ()
end


@view
func view_val{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }() -> (res: felt):
    let (val_now) = storage_felt.read()
    return (res=val_now)
end
