%lang starknet

func f() -> (res: felt) {
  return (res=12);
}

@external
func test_basic() -> () {
  let (fres) = f();
  assert fres = 12;
  %{
    print("Hello from the hint!")
    assert ids.fres == 12
  %}
  return ();
}
