%lang starknet

@external
func up() {
    %{
        declaration = declare("./build/main.json", config={"max_fee": "auto"})
        contract = deploy_contract(declaration.class_hash, config={"max_fee": "auto"})

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
