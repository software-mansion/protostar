%lang starknet

struct VoterInfo {
    a: felt,
    b: felt,
}

@external
func __setup__() {
    %{ max_examples(3) %}
    return ();
}

@external
func test_fails_on_non_felt_parameter(a: VoterInfo) {
    return ();
}
