use array::ArrayTrait;

#[test]
fn test_prepare() {
   let mut arr = ArrayTrait::new();
   arr.append(101);
   arr.append(202);
   arr.append(303);
   arr.append(405);
   arr.append(508);
   arr.append(613);
   arr.append(721);
   match prepare_tp(123, arr) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_prepare_tp() {
   let mut arr = ArrayTrait::new();
   arr.append(3);
   arr.append(2);
   arr.append(1);
   match prepare_tp(123, arr) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}

#[test]
fn test_prepare_no_args() {
   let mut arr = ArrayTrait::new();
   match prepare_tp(123, arr) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = array_new::<felt>();
         array_append::<felt>(ref data, x);
         panic(data)
      },
   }
}
