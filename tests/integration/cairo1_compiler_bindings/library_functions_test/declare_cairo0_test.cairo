#[test]
fn test_declare_cairo0() {
   match declare_cairo0('test') {
      Result::Ok(class_hash) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}
