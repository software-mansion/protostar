%lang starknet

@external
func up() {
    %{
        declaration = declare("./build/main.json")
        deploy_contract(declaration.class_hash)
    %}

    return ();
}

@external
func down() {
    %{ declare("./build/main.json") %}

    return ();
}
