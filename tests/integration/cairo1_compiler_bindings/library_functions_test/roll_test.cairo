#[test]
fn test_roll() {
   match roll(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
