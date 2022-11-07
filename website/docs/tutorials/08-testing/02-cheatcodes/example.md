# `example`

```python
def example(self, *args: Any, **kwargs: Any) -> None:
```

Parametrizes test with explicitly provided data.
You can provide multiple examples for one test.
In such a case, they are run sequentially.

`example` can be used next to the [`given`](./given.md) cheatcode.
In such a case, first all the `example`s are run and only then the the data from `given` is applied.
Otherwise, only the data from `example`s is applied.

:::info
This cheatcode is only available in [setup cases](../README.md#setup-case).
:::

:::info
`example` is not limited by [`max_examples`](./max-examples.md) and is not connected to it in any way.
:::

```cairo title="Example"
@external
func setup_less_equal_compare() {
    %{
        example(1, 2)
        # it affects the fuzzing strategy applied after all of the examples
        given(a = strategy.integers(15, 20), b = strategy.integers(10, 14))
        example(b=6, a=5)
    %}
    return ();
}

@external
func test_examples{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    # Tested against:
    # (1,2)
    # (3,4)
    # fuzzing: a = strategy.integers(15, 20), b = strategy.integers(10, 14) 
    assert_le(0, a);
    assert_le(0, b);
    assert_le(a, b);
    return ();
}
```
