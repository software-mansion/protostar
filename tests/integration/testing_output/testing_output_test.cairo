%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from tests.integration.testing_output.hash import hash_magic_numbers

@external
func test_printing_resource_usage_in_unit_testing_approach{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}():
    hash_magic_numbers()

    # assert in the pytest file
    return ()
end

@contract_interface
namespace HashContract:
    func hash_magic_numbers():
    end
end

@external
func test_printing_resource_usage_in_integration_testing_approach{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}():
    tempvar contract_address : felt
    %{ ids.contract_address = deploy_contract("./tests/integration/testing_output/hash.cairo").contract_address %}

    HashContract.hash_magic_numbers(contract_address)
    # assert in the pytest file
    return ()
end
