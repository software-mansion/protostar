use src::main::fib;
use src::mod1_cairo1::mod1_code::mod1f1;
use src::mod1_cairo1::mod1_code::mod1f2;
use src::mod2_cairo1::mod2_code::mod2f1;
use src::mod2_cairo1::mod2_code::mod2f2;

#[test]
fn test_modules() {
    let mod1f1_result = mod1f1(5);
    assert(mod1f1_result == 6, 'check mod1f1 result');

    let mod1f2_result = mod1f2(5);
    assert(mod1f2_result == 7, 'check mod1f2 result');

    let mod2f1_result = mod2f1(5);
    assert(mod2f1_result == 11, 'check mod2f1 result');

    let mod2f2_result = mod2f2(5);
    assert(mod2f2_result == 12, 'check mod2f2 result');
}
