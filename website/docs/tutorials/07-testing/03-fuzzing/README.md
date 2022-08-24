# Fuzzing

:::warning
This feature is actively developed and many new additions will land in future Protostar releases.
:::

Protostar tests can take parameters, which makes such tests to be run in a _fuzzing mode_.
In this mode, Protostar treats the test case parameters as a specification of the test case,
in the form of properties which it should satisfy,
and tests that these properties hold in numerous randomly generated input data.

This technique is often called _property-based testing_.
From the perspective of a user, the purpose of property-based testing is to make it easier for the
user to write better tests.

## Example

### The _Safe_

Let's see how fuzzing works in Protostar, by writing a test for an abstract "safe":

```cairo title="src/main.cairo"
%lang starknet
from starkware.cairo.common.math import assert_nn
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res : felt):
end

@external
func withdraw{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}(amount : felt):
    if amount == 0:
        return ()
    end

    let (res) = balance.read()
    let new_res = res - amount

    with_attr error_message("Cannot withdraw more than stored."):
        assert_nn(new_res)
    end

    balance.write(new_res)
    return ()
end

@constructor
func constructor{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}():
    balance.write(10000)
    return ()
end
```

### Unit testing

Let's first verify this function by writing a unit test in order to find the general property we are
testing for:

```cairo title="tests/test_main.cairo"
%lang starknet
from src.main import balance, withdraw
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_withdraw{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}():
    alloc_locals
    let (pre_balance_ref) = balance.read()
    local pre_balance = pre_balance_ref

    let amount = 1

    withdraw(amount)

    let (post_balance) = balance.read()
    assert post_balance = pre_balance - amount

    return ()
end
```

So far, so good. Running the test, we see it passes:

```text title="$ protostar test"
[PASS] tests/test_main.cairo test_withdraw (steps=129)
       range_check_builtin=1

11:28:43 [INFO] Test suites: 1 passed, 1 total
11:28:43 [INFO] Tests:       1 passed, 1 total
```

### Generalizing the test

This unit test performs checks if we can withdraw "some" amount from our safe.
However, can we be sure that it works for all amounts, not just this particular one?

The general property here is: given a safe balance, when we withdraw some amount from it,
we should get reduced balance in the safe, and it should not be possible to withdraw more than we
have.

Protostar will run any test that takes parameters in fuzz testing mode, so let's rewrite our unit
test.
We need to take the `Cannot withdraw more than stored.` error, so we also add a call to
the [`expect_revert`](../02-cheatcodes/expect-revert.md) cheatcode if needed.

```cairo title="tests/test_main.cairo
@external
func test_withdraw{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}(
    amount : felt
):
    alloc_locals
    let (pre_balance_ref) = balance.read()
    local pre_balance = pre_balance_ref

    %{
        if ids.amount > ids.pre_balance:
            expect_revert(error_message="Cannot withdraw more than stored.")
    %}
    withdraw(amount)

    let (post_balance) = balance.read()
    assert post_balance = pre_balance - amount

    return ()
end
```

If we run the test now, we can see that Protostar runs a fuzz test, but it fails for high values
of `amount`:

```text title="$ protostar test"
[FAIL] tests/test_main.cairo test_withdraw
[type] TRANSACTION_FAILED
[code] 39
[messages]:
— Cannot withdraw more than stored.
[details]:
<REDACTED>/starkware/cairo/common/math.cairo:40:5: Error at pc=0:0:
Got an exception while executing a hint.
    %{
    ^^
Cairo traceback (most recent call last):
tests/test_main.cairo:22:6: (pc=0:141)
func test_withdraw{syscall_ptr : felt*, range_check_ptr, pedersen_ptr : HashBuiltin*}(
     ^***********^
tests/test_main.cairo:36:5: (pc=0:125)
    withdraw(amount)
    ^**************^
Error message: Cannot withdraw more than stored.
<REDACTED>/src/main.cairo:23:9: (pc=0:63)
        assert_nn(new_res)
        ^****************^

Traceback (most recent call last):
  File "<REDACTED>/starkware/cairo/common/math.cairo", line 43, in <module>
    assert 0 <= ids.a % PRIME < range_check_builtin.bound, f'a = {ids.a} is out of range.'
AssertionError: a = 3618502788666131213697322783095070105282824848410658236509717448704103819025 is out of range.
[falsifying example]:
amount = 340282366920938463463374607431768211456

11:41:48 [INFO] Test suites: 1 failed, 1 total
11:41:48 [INFO] Tests:       1 failed, 1 total
11:41:48 [INFO] Seed:        4258368192
```




### Fixing the bug

The test fails because `amount` has `felt` type so its value can be negative. If smallest possible `felt` value is subtracted from `balance` it causes `felt` overflow.
The solution, is to check if `amount` is a negative number in `withdraw`, and adjust `test_withdraw`
appropriately:

```cairo title="src/main.cairo"
@external
func withdraw{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(amount : felt):
    with_attr error_message("Amount must be positive."):
        assert_nn(amount)
    end
    
    # ...
end
```

```cairo title="tests/test_main.cairo"
@external
func test_withdraw{
    syscall_ptr : felt*,
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
}(
    amount : felt
):
    # ...
    
    %{
        if not (0 <= ids.amount and ids.amount % PRIME < range_check_builtin.bound):
            expect_revert(error_message="Amount must be positive.")
        elif ids.amount > ids.pre_balance:
            expect_revert(error_message="Cannot withdraw more than stored.")
    %}
    withdraw(amount)
    
    # ...
end
```

And now, the test passes.
We can also observe the variance of resources usage, caused by the `if amount == 0:` branch in code.

```text title="$ protostar test"
[PASS] tests/test_main.cairo test_withdraw (fuzz_runs=100, steps=μ: 127, Md: 137, min: 84, max: 137)
       range_check_builtin=μ: 1.81, Md: 2, min: 1, max: 2

11:55:18 [INFO] Test suites: 1 passed, 1 total
11:55:18 [INFO] Tests:       1 passed, 1 total
11:55:18 [INFO] Seed:        3741774783
```

## Interpreting results

In fuzzing mode, the test is executed many times, hence test summaries are extended:

```
[PASS] tests/test_main.cairo test_withdraw (fuzz_runs=100, steps=μ: 127, Md: 137, min: 84, max: 137)
       range_check_builtin=μ: 1.81, Md: 2, min: 1, max: 2
```

Each resource counter presents a summary of observed values across all test runs:
- `μ` is the mean value of a used resource,
- `Md` is the median value of this resource,
- `min` is the lowest value observed,
- `max` is the highest value observed.

## Adjusting fuzzing quality

By default, Protostar tries to fail a test case within 100 examples.
The default value is chosen to suit a workflow where the test will be part of a suite that is
regularly executed locally or on a CI server,
balancing total running time against the chance of missing a bug.
The more complex code, the more examples are needed to find uncommon bugs.
To adjust number of input cases generated by the fuzzer,
call the [`max_examples`](../02-cheatcodes/max-examples.md) cheatcode within a
[setup hook](../README.md#setup-hooks).
