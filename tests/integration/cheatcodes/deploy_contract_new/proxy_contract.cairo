# Declare this file as a StarkNet contract and set the required
# builtins.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@storage_var
func target() -> (res : felt):
end

@external
func set_target{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        new_target : felt):
    target.write(new_target)
    return ()
end

@external
func increase_twice{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        amount : felt):
    let (target_contract) = target.read()
    BasicContract.increase_balance(contract_address=target_contract, amount=amount)
    BasicContract.increase_balance(contract_address=target_contract, amount=amount)
    return ()
end

@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        res : felt):
    let (target_contract) = target.read()
    let (res) = BasicContract.get_balance(contract_address=target_contract)
    return (res)
end
