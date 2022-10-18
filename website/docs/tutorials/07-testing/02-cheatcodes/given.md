# `given`

```python
def given(**kwargs: StrategyDescriptor) -> None:
```

Instructs the fuzzer to adopt a different fuzzing strategy for input parameters.
The built-in strategies are provided by the [`strategy`](./strategy.md) cheatcode,
and for a list of available strategies, see the [fuzzing strategies](../03-fuzzing/strategies.md)
guide page.

:::info
This cheatcode is only available in [setup cases](../README.md#setup-case).
:::

```cairo title="Example"
@external
func setup_less_equal_compare() {
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    return ();
}

@external
func test_less_equal_compare{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt) {
    assert_le(a, b);
    return ();
}
```

:::info
There is also the [`example`](./example.md) cheatcode that tests explicitly provided cases. It may come handy if you don't want to rely on randomization.
:::
