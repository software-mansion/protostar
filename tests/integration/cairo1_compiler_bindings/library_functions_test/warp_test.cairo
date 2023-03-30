#[test]
fn test_warp() {
   match warp(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}
