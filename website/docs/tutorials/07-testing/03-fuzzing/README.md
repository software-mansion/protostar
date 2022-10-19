# Fuzzing

:::warning
This feature is actively developed and many new additions will land in future Protostar releases.
:::

In order to use the _fuzzing mode_, you have to use the [`given`](../02-cheatcodes/given.md) cheatcode.
In the _fuzzing mode_, Protostar treats the test case parameters as a specification of the test case,
in the form of properties which it should satisfy,
and tests that these properties hold in numerous randomly generated input data.

This technique is often called _property-based testing_.
From the perspective of a user, the purpose of property-based testing is to make it easier for the
user to write better tests.

Fuzzer input parameters are selected according to a _fuzzing strategy_ associated with each
parameter.
Protostar offers various strategies tailored for specific use cases, check out
the [Strategies](./strategies.md) page for more information.
Associating a fuzzing strategy to a parameter is done using the [`given`](../02-cheatcodes/given.md)
cheatcode, which is only available within [setup cases][setup-case].

## Example

### The _Safe_

Let's see how fuzzing works in Protostar, by writing a test for an abstract "safe":

```cairo title="src/main.cairo"
%lang starknet
from starkware.cairo.common.math import assert_nn
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@external
func withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}(amount: felt) {
    if (amount == 0) {
        return ();
    }

    let (res) = balance.read();
    let new_res = res - amount;

    with_attr error_message("Cannot withdraw more than stored.") {
        assert_nn(new_res);
    }

    balance.write(new_res);
    return ();
}
```

### Unit testing

Let's first verify this function by writing a unit test in order to find the general property we are
testing for:

```cairo title="tests/test_main.cairo"
%lang starknet
from src.main import balance, withdraw
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func setup_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    balance.write(10000);
    return ();
}

@external
func test_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    alloc_locals;
    let (pre_balance_ref) = balance.read();
    local pre_balance = pre_balance_ref;

    let amount = 1;

    withdraw(amount);

    let (post_balance) = balance.read();
    assert post_balance = pre_balance - amount;

    return ();
}
```

So far, so good. Running the test, we see it passes:

```text title="$ protostar test"
12:14:47 [INFO] Collected 1 suite, and 1 test case (0.077 s)
[PASS] tests/test_main.cairo test_withdraw (time=1.19s, steps=129)
       range_check_builtin=1

12:14:51 [INFO] Test suites: 1 passed, 1 total
12:14:51 [INFO] Tests:       1 passed, 1 total
12:14:51 [INFO] Seed:        2917010406
12:14:51 [INFO] Execution time: 5.34 s
```

### Generalizing the test

This unit test performs checks if we can withdraw "some" amount from our safe.
However, can we be sure that it works for all amounts, not just this particular one?

The general property here is: given a safe balance, when we withdraw some amount from it, we should
get reduced balance in the safe, and it should not be possible to withdraw more than we have.

In order to run our test in the fuzz testing mode, we need to use the [`given`](../02-cheatcodes/given.md)
cheatcode. Let's apply this:

```cairo title="tests/test_main.cairo"
%lang starknet
from src.main import balance, withdraw
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func setup_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    %{ given(amount = strategy.felts()) %}

    balance.write(10000);
    return ();
}

@external
func test_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}(amount: felt) {
    alloc_locals;
    let (pre_balance_ref) = balance.read();
    local pre_balance = pre_balance_ref;

    withdraw(amount);

    let (post_balance) = balance.read();
    assert post_balance = pre_balance - amount;

    return ();
}
```

This test is being run using the [`felts`](./strategies.md#strategyfelts) strategy.
By default, it tries to apply all possible `felt` values.

When the test is run now, we can see that it fails for values larger than the amount we stored
in [`setup_withdraw` hook][setup-case]:

```text title="$ protostar test"
12:23:55 [INFO] Collected 1 suite, and 1 test case (0.076 s)
[FAIL] tests/test_main.cairo test_withdraw (time=7.69s, fuzz_runs=77)
[type] TRANSACTION_FAILED
[code] 43
[messages]:
— Cannot withdraw more than stored.
[details]:
<REDACTED>/starkware/cairo/common/math.cairo:42:5: Error at pc=0:0:
Got an exception while executing a hint.
    %{
    ^^
Cairo traceback (most recent call last):
tests/test_main.cairo:16:6: (pc=0:141)
func test_withdraw{
     ^***********^
tests/test_main.cairo:25:6: (pc=0:125)
     withdraw(amount);
     ^**************^
Error message: Cannot withdraw more than stored.
<REDACTED>/src/main.cairo:19:9: (pc=0:63)
        assert_nn(new_res);
        ^****************^

Traceback (most recent call last):
  File "<REDACTED>/starkware/cairo/common/math.cairo", line 45, in <module>
    assert 0 <= ids.a % PRIME < range_check_builtin.bound, f'a = {ids.a} is out of range.'
AssertionError: a = 3618502788666131213697322783095070105623107215331596699973092056135872020480 is out of range.
[falsifying example]:
amount = 10001


12:24:06 [INFO] Test suites: 1 failed, 1 total
12:24:06 [INFO] Tests:       1 failed, 1 total
12:24:06 [INFO] Seed:        2965326707
12:24:06 [INFO] Execution time: 11.95 s
```

We need to take the `Cannot withdraw more than stored` error into consideration, so we also add a
call to the [`expect_revert`](../02-cheatcodes/expect-revert.md) cheatcode if needed.

```cairo title="tests/test_main.cairo"
@external
func test_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}(amount: felt) {
    alloc_locals;
    let (pre_balance_ref) = balance.read();
    local pre_balance = pre_balance_ref;

    %{
        if ids.amount > ids.pre_balance:
            expect_revert(error_message="Cannot withdraw more than stored.")
    %}
    withdraw(amount);

    let (post_balance) = balance.read();
    assert post_balance = pre_balance - amount;

    return ();
}
```

If we run the test now, we can see that Protostar runs a fuzz test, but it fails for high values
of `amount`:

```text title="$ protostar test"
12:25:23 [INFO] Collected 1 suite, and 1 test case (0.075 s)
[FAIL] tests/test_main.cairo test_withdraw (time=3.04s, fuzz_runs=21)
Expected an exception matching the following error:
[error_messages]:
— Cannot withdraw more than stored.
[falsifying example]:
amount = 3618502788666131213697322783095070105623107215331596699973092056135872020480


12:25:29 [INFO] Test suites: 1 failed, 1 total
12:25:29 [INFO] Tests:       1 failed, 1 total
12:25:29 [INFO] Seed:        1746010604
12:25:29 [INFO] Execution time: 7.34 s
```

### Fixing the bug

The test fails because `amount` has `felt` type, so it can overflow when subtracting.
In particular, it is certain, that the overflow will happen if you try to
withdraw `FIELD_PRIME - 1` (which is the number fuzzer found!).
Although this bug should be fixed within the contract, for the purpose of this tutorial we will do
it differently:
we will instruct the fuzzer to avoid numbers outside of `range_check` builtin boundary.

The [`felts`](./strategies.md#strategyfelts) strategy accepts a keyword argument `rc_bound`
which narrows the range of values to be safe to be passed to range check-based assertions:

```cairo title="src/main.cairo"
@external
func setup_withdraw{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    %{ given(amount = strategy.felts(rc_bound=True)) %}

    balance.write(10000);
    return ();
}
```

And now, the test passes.
We can also observe the variance of resources usage, caused by the `if amount == 0:` branch in
contract code.

```text title="$ protostar test"
12:27:23 [INFO] Collected 1 suite, and 1 test case (0.075 s)
[PASS] tests/test_main.cairo test_withdraw (time=9.49s, fuzz_runs=100, steps=μ: 118.84, Md: 131, min: 78, max: 131)
       range_check_builtin=μ: 1, Md: 1, min: 1, max: 1

12:27:35 [INFO] Test suites: 1 passed, 1 total
12:27:35 [INFO] Tests:       1 passed, 1 total
12:27:35 [INFO] Seed:        3287645654
12:27:35 [INFO] Execution time: 13.46 s
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
[setup hook][setup-hook].

[setup-case]: ../README.md#setup-case

[setup-hook]: ../README.md#setup-hooks
