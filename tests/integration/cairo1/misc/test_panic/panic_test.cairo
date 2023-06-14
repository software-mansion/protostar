use array::ArrayTrait;

#[test]
fn test_panic_when_felt252_not_short_str() {
    let temp = 1234;
    assert(1 == temp, temp);
}

#[test]
fn test_panic_with_felt252_max_val() {
    let mut data = ArrayTrait::new();
    data.append(3618502788666131213697322783095070105623107215331596699973092056135872020480); // felt252 max val

    panic(data);
}
