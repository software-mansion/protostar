# `assume`
```python
def assume(condition: bool) -> None:
```
`assume(condition)` skips testing against the given example if the `condition` is `False`.

:::warning
This cheatcode is only available in [fuzz tests](../03-fuzzing/README.md).
:::

```cairo
%lang starknet

@external
func test_function_that_takes_nonzero_argument{syscall_ptr: felt*, range_check_ptr}(value) {
    %{ assume(ids.value != 0) %}

    // ...

    return ();
}
```

:::tip
You should use `assume` only for narrow checks, as it can slow down the tests significantly due to
the need for more specific inputs.
If you need to restrict example space by a vast range, consider
using [fuzzing strategies](../03-fuzzing/strategies.md) instead.
:::
