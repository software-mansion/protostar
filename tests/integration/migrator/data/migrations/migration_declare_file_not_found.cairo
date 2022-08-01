%lang starknet

@external
func up():
    %{ declare("./NOT_EXISTING_FILE.json") %}

    return ()
end
