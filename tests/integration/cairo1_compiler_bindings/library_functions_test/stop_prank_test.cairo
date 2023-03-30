#[test]
fn test_stop_prank() {
    match stop_prank(123) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}
