#[test]
fn test_warp() {
   match warp(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
