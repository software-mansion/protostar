from starkware.cairo.common.math import assert_not_zero, assert_not_equal

func test_stop_roll(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert roll(ids.deployed_contract_address, 123).err_code == 0
    %}

    assert_not_zero(deployed_contract_address);

    local block_nb;
    %{
        ids.block_nb = call(ids.deployed_contract_address, "block_number_getter").ok[0]
    %}

    assert block_nb = 123;

    %{
        assert stop_roll(ids.deployed_contract_address).err_code == 0
    %}

    local block_nb_after_stopping;
    %{
        ids.block_nb_after_stopping = call(ids.deployed_contract_address, "block_number_getter").ok[0]
    %}

    assert_not_equal(block_nb_after_stopping, 123);

    return ();
}

func test_stop_roll_with_invoke(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("./src/main.cairo").ok.contract_address
        assert roll(ids.deployed_contract_address, 123).err_code == 0
    %}
    assert_not_zero(deployed_contract_address);

    %{ assert invoke(ids.deployed_contract_address, "block_number_setter").err_code == 0 %}

    local stored_block_number;
    %{ ids.stored_block_number = call(ids.deployed_contract_address, "stored_block_number_getter").ok[0] %}
    assert stored_block_number = 123;


    local stored_block_number_after_stopping;
    %{
        assert stop_roll(ids.deployed_contract_address).err_code == 0
        assert invoke(ids.deployed_contract_address, "block_number_setter").err_code == 0
        ids.stored_block_number_after_stopping = call(ids.deployed_contract_address, "stored_block_number_getter").ok[0]
    %}

    assert_not_equal(stored_block_number_after_stopping, 123);

    return ();
}
