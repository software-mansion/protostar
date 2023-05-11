use array::ArrayTrait;

#[test]
fn test_start_roll() {
   match start_roll(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
