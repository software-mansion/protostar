%lang starknet

func rec(step: felt) -> felt {
    if (step == 0) {
        return 0;
    }

    return rec(step - 1);
}

@external
func test_max_step() {
    rec(50);
    return ();
}
