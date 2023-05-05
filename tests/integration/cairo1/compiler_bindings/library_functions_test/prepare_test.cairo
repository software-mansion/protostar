use array::ArrayTrait;

#[test]
fn test_prepare() {
   let mut arr = ArrayTrait::new();
   arr.append(101);
   arr.append(202);
   arr.append(613);
   arr.append(721);
   match prepare(123, arr) {
      Result::Ok(PreparedContract{contract_address, class_hash, constructor_calldata}) => {
        assert(constructor_calldata.len() == 4_u32, 'check constructor_calldata');
        assert(*constructor_calldata.at(0_usize) == 101, 'check constructor_calldata[0]');
        assert(*constructor_calldata.at(1_usize) == 202, 'check constructor_calldata[1]');
        assert(*constructor_calldata.at(2_usize) == 613, 'check constructor_calldata[2]');
        assert(*constructor_calldata.at(3_usize) == 721, 'check constructor_calldata[3]');
        assert(contract_address == 111, 'check contract_address');
        assert(class_hash == 222, 'check class_hash');
        ()
      },
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}

#[test]
fn test_prepare_impl() {
   let mut arr = ArrayTrait::new();
   arr.append(3);
   arr.append(2);
   arr.append(1);
   match prepare_impl(123, arr) {
      Result::Ok((constructor_calldata, contract_address, class_hash)) => {
        assert(constructor_calldata.len() == 3_u32, 'check constructor_calldata');
        assert(*constructor_calldata.at(0_usize) == 3, 'check constructor_calldata[0]');
        assert(*constructor_calldata.at(1_usize) == 2, 'check constructor_calldata[1]');
        assert(*constructor_calldata.at(2_usize) == 1, 'check constructor_calldata[2]');
        assert(contract_address == 0, 'check contract_address');
        assert(class_hash == 444, 'check class_hash');
        ()
      },
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}

#[test]
fn test_prepare_no_args() {
   let mut arr = ArrayTrait::new();
   match prepare(123, arr) {
      Result::Ok(PreparedContract{contract_address, class_hash, constructor_calldata}) => {
        assert(constructor_calldata.len() == 0_u32, 'check constructor_calldata');
        assert(contract_address == 999, 'check contract_address');
        assert(class_hash == 345, 'check class_hash');
        ()
      },
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
