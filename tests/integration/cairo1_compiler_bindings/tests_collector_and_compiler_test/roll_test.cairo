#[test]
fn test_cheatcode_caller() {
   roll(1, 2)
}
#[test]
fn test_cheatcode_caller_twice() {
   roll(1, 2);
   roll(1, 2)
}
#[test]
fn test_cheatcode_caller_three() {
   roll(1, 2);
   roll(1, 2);
   roll(1, 2)
}