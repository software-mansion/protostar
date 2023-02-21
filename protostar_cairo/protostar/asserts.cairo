from protostar._utils import use_signed_int_hint

// ---------------------------------- EQUAL ---------------------------------
func assert_eq(a: felt, to: felt) {
    %{ assert ids.a == ids.to, f"a = {ids.a} is not equal to {ids.to}" %}
    return ();
}

func assert_not_eq(a: felt, to: felt) {
    %{ assert ids.a != ids.to, f"a = {ids.a} is equal to {ids.to}" %}
    return ();
}

// ---------------------------------- LESS ----------------------------------
func assert_signed_lt(a: felt, than: felt) {
    use_signed_int_hint();
    %{ assert signed_int(ids.a) < signed_int(ids.than), f"a = {signed_int(ids.a)} is not less than {signed_int(ids.than)}" %}
    return ();
}

func assert_unsigned_lt(a: felt, than: felt) {
    %{ assert ids.a < ids.than, f"a = {ids.a} is not less than {ids.than}" %}
    return ();
}

func assert_signed_le(a: felt, to: felt) {
    use_signed_int_hint();
    %{ assert signed_int(ids.a) <= signed_int(ids.to), f"a = {signed_int(ids.a)} is not less or equal to {signed_int(ids.to)}" %}
    return ();
}

func assert_unsigned_le(a: felt, to: felt) {
    %{ assert ids.a <= ids.to, f"a = {ids.a} is not less or equal to {ids.to}" %}
    return ();
}

// --------------------------------- GREATER --------------------------------
func assert_signed_gt(a: felt, than: felt) {
    use_signed_int_hint();
    %{ assert signed_int(ids.a) > signed_int(ids.than), f"a = {signed_int(ids.a)} is not greater than {signed_int(ids.than)}" %}
    return ();
}

func assert_unsigned_gt(a: felt, than: felt) {
    %{ assert ids.a > ids.than, f"a = {ids.a} is not greater than {ids.than}" %}
    return ();
}

func assert_signed_ge(a: felt, to: felt) {
    use_signed_int_hint();
    %{ assert signed_int(ids.a) >= signed_int(ids.to), f"a = {signed_int(ids.a)} is not greater or equal to {signed_int(ids.to)}" %}
    return ();
}

func assert_unsigned_ge(a: felt, to: felt) {
    %{ assert ids.a >= ids.to, f"a = {ids.a} is not greater or equal to {ids.to}" %}
    return ();
}
