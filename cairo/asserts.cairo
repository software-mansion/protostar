from starkware.cairo.common.math import assert_le as _assert_le, split_felt

func assert_eq(a : felt, to : felt):
    %{ assert ids.a == ids.to, f"a = {ids.a} is not equal to {ids.to}" %}
    return ()
end

func assert_not_eq(a : felt, to : felt):
    %{ assert ids.a != ids.to, f"a = {ids.a} is equal to {ids.to}" %}
    return ()
end

func assert_lt(a : felt, than : felt):
    %{ assert ids.a < ids.than, f"a = {ids.a} is not less than {ids.than}" %}
    return ()
end

func assert_le(a : felt, to : felt):
    %{ assert ids.a <= ids.to, f"a = {ids.a} is not less or equal to {ids.to}" %}
    return ()
end

func assert_gt(a : felt, than : felt):
    %{ assert ids.a > ids.than, f"a = {ids.a} is not greater than {ids.than}" %}
    return ()
end

func assert_ge(a : felt, to : felt):
    %{ assert ids.a >= ids.to, f"a = {ids.a} is not greater or equal to {ids.to}" %}
    return ()
end
