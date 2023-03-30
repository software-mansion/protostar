#[test]
fn test_roll() {
   match roll(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}
