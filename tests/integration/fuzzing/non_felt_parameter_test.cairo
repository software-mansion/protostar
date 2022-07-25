%lang starknet

struct VoterInfo:
    member a: felt
    member b: felt
end

@external
func test_fails_on_non_felt_parameter(a : VoterInfo):
    return ()
end
