# `given`

```python
def given(**kwargs: StrategyDescriptor) -> None:
```

Instructs the fuzzer to adopt a new fuzzing strategy to input parameters.
The built-in strategies are provided by the [`strategy`](./strategy.md) cheatcode, and a list of
available strategies, see the [fuzzing strategies](../03-fuzzing/strategies.md) guide page.

:::warning
This cheatcode is only available in [fuzz tests](../fuzzing).
:::

```cairo title="Example"
@external
func test_integers{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    assert_le(a, b)
    return ()
end
```

## Performance caveats

While it is possible to call `given()` multiple times in a test case,
it is recommended to always do it once in a test case,
and configure multiple input parameters by passing many arguments to the cheatcode.

Due to Cairo language limitations and resulting therefrom implementation details,
each call to the `given` cheatcode causes the fuzzer to restart immediately with fresh state
and newly set strategies,
with the maximum number of tested examples reduced by the amount used in previous runs.
Think of this as Protostar _learning a new strategy_ (this terminology is used internally).
The consequence of this process is that each next _learning step_ effectively reduces a space
of explored input parameters values, thus making the test less effective.

Avoid binding fuzzing strategies to input parameters values or any other external state,
such as random data of system time.
This would cause non-deterministic behaviour of strategy learning and may yield bad results.
Protostar detects if a test exhausts the maximum number of fuzzing runs and reports an appropriate
error.
