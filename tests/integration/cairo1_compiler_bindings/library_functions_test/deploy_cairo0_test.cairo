use array::ArrayTrait;

#[test]
fn test_deploy_cairo0() {
   let mut arr = ArrayTrait::new();
   arr.append(1);
   arr.append(2);
   match deploy_cairo0(PreparedContract { contract_address: 123, class_hash: 234, constructor_calldata: arr }) {
      Result::Ok(deployed_contract_address) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_deploy_cairo0_no_args() {
   let mut arr = ArrayTrait::new();
   match deploy_cairo0(PreparedContract { contract_address: 123, class_hash: 234, constructor_calldata: arr }) {
      Result::Ok(deployed_contract_address) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_deploy_tp_cairo0() {
   let mut arr = ArrayTrait::new();
   arr.append(5);
   arr.append(4);
   arr.append(2);
   match deploy_tp_cairo0(123, 234, arr) {
      Result::Ok(deployed_contract_address) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
