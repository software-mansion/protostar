use array::ArrayTrait;

#[test]
fn test_stop_prank() {
    match stop_prank(123) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
