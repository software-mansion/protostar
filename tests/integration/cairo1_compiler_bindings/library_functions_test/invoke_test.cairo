use array::ArrayTrait;

#[test]
fn test_invoke() {
   let mut arr = ArrayTrait::new();
   arr.append(101);
   arr.append(202);
   arr.append(303);
   arr.append(405);
   arr.append(508);
   arr.append(613);
   arr.append(721);
   match invoke(123, 'test', arr) {
      Result::Ok(class_hash) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

