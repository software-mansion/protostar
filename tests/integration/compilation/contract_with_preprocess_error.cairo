%lang starknet

func two_arg_func(a: felt, b: felt) {
    return ();
}

@external
func test_one() {
    two_arg_func(1, 2, 3);
    return ();
}
