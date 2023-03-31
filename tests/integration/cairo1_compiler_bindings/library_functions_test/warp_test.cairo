use array::ArrayTrait;

#[test]
fn test_warp() {
   match warp(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
