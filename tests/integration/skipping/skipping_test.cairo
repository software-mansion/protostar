%lang starknet

@external
func test_skip():
    %{ skip(True, "AAA") %}
    return ()
end

@external
func test_skip_false():
    %{ skip(False, "BBB") %}
    return ()
end

@external
func test_skip_no_reason():
    %{ skip(True) %}
    return ()
end

@external
func test_skip_no_input():
    %{ skip() %}
    return ()
end

@external
func test_skip_failed():
    %{ skip(True, "CCC") %}
    assert 0 = 1
    return ()
end

@external
func test_skip_false_failed():
    %{ skip(False, "DDD") %}
    assert 0 = 1
    return ()
end
