%lang starknet

@external
func up():
    %{ deploy_contract("./build/main_with_constructor.json", [42]) %}

    return ()
end
