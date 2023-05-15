use array::ArrayTrait;

#[test]
fn test_mock_call() {
   let mut arr = ArrayTrait::new();
   arr.append(121);
   arr.append(122);
   arr.append(123);
   arr.append(124);
   match mock_call(123, 'test', @arr) {
      Result::Ok(class_hash) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}

#[test]
fn test_mock_call_no_args() {
   let mut arr = ArrayTrait::new();
   match mock_call(123, 'test', @arr) {
      Result::Ok(class_hash) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}

