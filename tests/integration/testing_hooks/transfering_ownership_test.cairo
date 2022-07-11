%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace Ownable:
    func transfer_ownership(new_owner : felt):
    end

    func owner() -> (owner : felt):
    end
end

@external
func __setup__():
    %{ context.account_address = deploy_contract("./tests/data/cairo_contracts/src/openzeppelin/account/Account.cairo", {"public_key": 0}).contract_address %}
    %{ context.ownable_address = deploy_contract("./tests/data/cairo_contracts/src/openzeppelin/access/ownable.cairo").contract_address %}

    return ()
end

@external
func test_transfering_ownership{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        ):
    alloc_locals
    local ownable_address
    local account_address

    %{ ids.ownable_address = context.ownable_address %}
    %{ ids.account_address = context.account_address %}

    Ownable.transfer_ownership(ownable_address, account_address)

    # let (owner) = Ownable.owner(ownable_address)
    # assert owner = 42
    return ()
end
