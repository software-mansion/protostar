use array::ArrayTrait;

// TODO (pmagiera)
#[test]
fn test_deploying_pipeline_with_path() {
   let mut arr = ArrayTrait::new();
   arr.append(3);
   arr.append(2);
   arr.append(1);

    let class_hash = match declare_cairo0('basic_contract_cairo0') {
        Result::Ok(x)  => x,
        Result::Err(x) => {
            let mut data = ArrayTrait::new();
            data.append(x);
            panic(data)
        },
    };

    assert(class_hash != 0, 'class_hash != 0');

    let prepared_contract = match prepare_cairo0(
        class_hash, arr
    ) {
        Result::Ok(x) => drop(x),
        Result::Err(x) => {
            let mut data = ArrayTrait::new();
            data.append(x);
            panic(data)
      },
    };
}
