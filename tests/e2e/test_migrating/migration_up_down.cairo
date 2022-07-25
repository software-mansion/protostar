%lang starknet

@external
func up():
    %{ deploy_contract("./build/main.json", [21]) %}

    return ()
end

@external
func down():
    %{ declare("./build/main.json") %}

    return ()
end
