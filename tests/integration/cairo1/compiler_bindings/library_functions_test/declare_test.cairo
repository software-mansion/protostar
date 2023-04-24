use array::ArrayTrait;

#[test]
fn test_declare() {
   match declare('test') {
      Result::Ok(class_hash) => {
        assert(class_hash == 123, 'check class_hash');
        ()
      },
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
