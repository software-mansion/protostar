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
      Result::Ok(return_data) => {
        assert(return_data.len() == 0_u32, 'Unexpected span length.');
        //assert(return_data.at(0_usize) != 1000, 'array[0] == 10');
        //assert(*return_data.get(0_u32) == Option::Some(0), 'return data check');
        ()
      },
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
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
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
