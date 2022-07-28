%lang starknet

@external
func up():
    %{ declare("./build/main_with_constructor.json") %}

    return ()
end
