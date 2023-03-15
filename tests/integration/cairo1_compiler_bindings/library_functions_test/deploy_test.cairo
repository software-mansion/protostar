use array::ArrayTrait;

#[test]
fn test_deploy() {
   let mut arr = ArrayTrait::new();
   arr.append(1);
   arr.append(2);
   match deploy(123, 123, arr) {
      Result::Ok(deployed_contract_address) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_deploy_wrapper() {
   let mut arr = ArrayTrait::new();
   arr.append(1);
   arr.append(2);
   match deploy_wrapper(PreparedContract { address: 123, class_hash: 123, constructor_calldata: arr }) {
      Result::Ok(deployed_contract_address) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}