use array::ArrayTrait;

#[test]
fn test_call() {
   let mut arr = ArrayTrait::new();
   arr.append(101);
   arr.append(613);
   arr.append(721);
   arr.append(508);
   arr.append(405);
   match call(123, 'test', arr) {
      Result::Ok(return_data) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_call_no_args() {
   let mut arr = ArrayTrait::new();
   match call(123, 'test', arr) {
      Result::Ok(return_data) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt252>();
         array_append::<felt252>(ref data, x);
         panic(data)
      },
   }
}
