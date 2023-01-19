from starkware.cairo.common.math import assert_not_zero

func test_roll(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").contract_address
        roll(ids.deployed_contract_address, 123)
    %}

    assert_not_zero(deployed_contract_address);

    local block_nb;
    %{
        ids.block_nb = call(ids.deployed_contract_address, "block_number_getter")[0]
    %}

    assert block_nb = 123;

    return ();
}

func test_roll_with_invoke(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").contract_address
        roll(ids.deployed_contract_address, 123)
    %}
    assert_not_zero(deployed_contract_address);

    // Set the timestamp to rolled value
    %{ invoke(ids.deployed_contract_address, "block_number_setter") %}

    // Retrieve stored value
    local stored_block_number;
    %{ ids.stored_block_number = call(ids.deployed_contract_address, "stored_block_number_getter")[0] %}
    assert stored_block_number = 123;
    return ();
}