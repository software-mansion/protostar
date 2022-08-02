# `assume`
```python
def assume(condition: bool) -> None:
```
`assume(condition)` skips testing against the given example if the `condition` is `False`.

:::warning
This cheatcode is only available in [fuzz tests](../fuzzing).
:::

```cairo
%lang starknet

@external
func test_function_that_takes_nonzero_argument{syscall_ptr : felt*, range_check_ptr}(value):
    %{ assume(ids.value != 0) %}

    # ...

    return ()
end
```

:::tip
You should use `assume` only for narrow checks, as it can slow down the tests significantly due to the need for more specific inputs.
:::
