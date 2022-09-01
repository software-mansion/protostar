%lang starknet

@external
func up() {
    %{ deploy_contract("./build/main.json") %}

    return ();
}

@external
func down() {
    %{ declare("./build/main.json") %}

    return ();
}
