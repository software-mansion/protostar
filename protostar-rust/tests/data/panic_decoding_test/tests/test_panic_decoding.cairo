use array::ArrayTrait;

#[test]
fn test_panic_decoding() {
    let max_felt = 3618502788666131213697322783095070105623107215331596699973092056135872020480;

    let mut arr = ArrayTrait::new();
    arr.append(123);
    arr.append('aaa');
    arr.append(max_felt);
    arr.append(152);
    arr.append(124);
    arr.append(149);

    panic(arr);
}
