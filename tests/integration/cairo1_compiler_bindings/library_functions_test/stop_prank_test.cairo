#[test]
fn test_stop_prank() {
    match stop_prank(123) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
