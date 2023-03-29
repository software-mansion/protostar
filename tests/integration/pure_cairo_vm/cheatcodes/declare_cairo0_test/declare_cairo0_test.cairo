#[test]
fn test_declaring_contract(){
    match declare_cairo0('basic_contract_cairo0') {
      Result::Ok(class_hash) => {
        assert(class_hash != 0, 'class_hash != 0');
      },
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_failing_to_declare_contract(){
    match declare_cairo0('nonexisting_contract') {
      Result::Ok(class_hash) => {
        assert(class_hash != 0, 'class_hash != 0');
      },
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_declaring_broken_contract(){
    match declare_cairo0('broken_syntax_contract') {
      Result::Ok(class_hash) => {
        assert(class_hash != 0, 'class_hash != 0');
      },
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}