use result::ResultTrait;

#[test]
fn test_cheatcode_caller() {
   roll(1, 2).unwrap();
}

#[test]
fn test_cheatcode_caller_twice() {
   roll(1, 2).unwrap();
   roll(1, 2).unwrap()
}

#[test]
fn test_cheatcode_caller_three() {
   roll(1, 2).unwrap();
   roll(1, 2).unwrap();
   roll(1, 2).unwrap()
}
