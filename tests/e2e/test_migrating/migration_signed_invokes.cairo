%lang starknet

@external
func up() {
    %{
        contract  = deploy_contract("./build/main.json")

        invoke(contract.contract_address, "put", { "value": 69 }, config={"max_fee": "auto"})
        invoke(contract.contract_address, "put", { "value": 69 }, config={"max_fee": 1000900000000000, "wait_for_acceptance": True})

        ret_object = call(contract.contract_address, "get")

        assert ret_object.res == 69
    %}

    return ();
}

@external
func down() {
    %{ declare("./build/main.json") %}

    return ();
}
