use array::ArrayTrait;

#[test]
fn test_roll() {
   match roll(1, 2) {
      Result::Ok(_) => (),
      Result::Err(x) => {
         let mut data = ArrayTrait::new();
         data.append(x);
         panic(data)
      },
   }
}
