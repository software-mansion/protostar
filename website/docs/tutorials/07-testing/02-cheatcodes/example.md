# `example`

```python
def example(self, *args: Any, **kwargs: Any) -> None:
```

This is an addition to the [`given`](./given.md) cheatcode, but, due to how the protostar works,
`given` cheatcode does not have to be used in order to invoke `example`.
While `given` runs tests with multiple, randomly generated data sets,
`example` takes certain values and runs tests using them.
Tests with the data specified in `example` will always be run before applying the data from `given`.

Multiple `example`s can be used for one test. In such a case, all of them will be run sequentially,
only after that allowing `given` to run.

`example` can be used either as positional or keyword based (but these cannot be mixed in a single call).

:::warning
This cheatcode is only available in [setup cases](../README.md#setup-case).
:::

```cairo title="Example"
@external
func setup_less_equal_compare() {
    %{
        example(1, 2)
        example(2, 3)

        given(a = strategy.integers(15, 20), b = strategy.integers(10, 14))

        example(a=3, b=4)
        example(b=6, a=5)
    %}
    return ();
}

@external
func test_examples{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    assert_le(0, a);
    assert_le(0, b);
    assert_le(a, b);
    return ();
}
```
