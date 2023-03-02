use array::ArrayTrait;

#[test]
fn test_panic() {
   let mut arr = ArrayTrait::new();
   arr.append(101);
   arr.append(202);
   arr.append(303);
   panic(arr);
}

