# `reject`

```python
def reject() -> None:
```

`reject()` skips testing against the given example.

It is equivalent to `assume(False)`.

:::warning
This cheatcode is only available in [fuzz tests](../03-fuzzing/README.md).
:::

```cairo title="Example"
%lang starknet

@external
func test_function_that_takes_nonzero_argument(value) {
    if (value == 0) {
        %{ reject() %}
        assert 0 = 0;
    }

    // ...

    return ();
}
```

:::tip
The `reject` cheatcode should only be used for narrow checks dependent on logic written in Cairo,
as it can slow down the tests significantly due to the need for more specific inputs.
If the condition is independent of test code, using
the [`filter`](../03-fuzzing/strategies.md#filtering) method
on [fuzzing strategies](../03-fuzzing/strategies.md) is preferred.
If you need to restrict example space by a vast range, consider using more
[sophisticated fuzzing strategies](../03-fuzzing/strategies.md#core-strategies) instead.
:::
