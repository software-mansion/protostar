%lang starknet

@external
func up():
    %{ deploy_contract("./build/main_with_constructor.json", [21]) %}

    return ()
end

@external
func down():
    %{ declare("./build/main_with_constructor.json") %}

    return ()
end
