use result::ResultTrait;

#[test]
fn test_cheatcode_caller() {
   start_roll(1, 2).unwrap();
}

#[test]
fn test_cheatcode_caller_twice() {
   start_roll(1, 2).unwrap();
   start_roll(1, 2).unwrap()
}

#[test]
fn test_cheatcode_caller_three() {
   start_roll(1, 2).unwrap();
   start_roll(1, 2).unwrap();
   start_roll(1, 2).unwrap()
}
