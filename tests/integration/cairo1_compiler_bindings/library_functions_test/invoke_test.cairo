use array::ArrayTrait;

#[test]
fn test_invoke() {
   let mut arr = ArrayTrait::new();
   arr.append(10);
   arr.append(11);
   arr.append(12);
   match invoke(123, 'test', arr) {
      Result::Ok(class_hash) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

