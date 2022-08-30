%lang starknet

@external
func up():
    %{
        contract  = deploy_contract("./build/main.json")

        invoke(contract.contract_address, "put", { "value": 69 }, config={"auto_estimate_fee": True})
        invoke(contract.contract_address, "put", { "value": 69 }, config={"max_fee": 10000, wait_for_acceptance: True})

        ret_object = call(contract.contract_address, "get")

        assert ret_object.res == 69
    %}

    return ()
end

@external
func down():
    %{ declare("./build/main.json") %}

    return ()
end
