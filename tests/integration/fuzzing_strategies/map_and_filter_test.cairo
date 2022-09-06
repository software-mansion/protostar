%lang starknet

from starkware.cairo.common.math import assert_in_range

@external
func __setup__():
    %{ max_examples(3) %}
    return ()
end

@external
func setup_chaining():
    %{
        given(
               a = strategy.felts().filter(lambda x:  17 < x < 100).map(lambda x: -x).filter(lambda x: x < -20) 
           )
    %}
    return ()
end

@external
func test_chaining(a):
    assert a = 3
    return ()
end

@external
func setup_filtering():
    %{
        given(
               a = strategy.one_of( strategy.integers().filter(lambda x: 100 <= x <= 1000) ) 
           )
    %}
    return ()
end

@external
func test_filtering{range_check_ptr}(a):
    assert_in_range(a, 100, 1000)
    return ()
end

@external
func setup_mapping():
    %{
        given(
               a = strategy.one_of( strategy.integers().map(lambda x: 3) ) 
           )
    %}
    return ()
end

@external
func test_mapping(a):
    assert a = 3
    return ()
end
