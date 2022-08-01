# `assume`
```python
def assume(condition: bool) -> None:
```
`assume(condition)` works similarly to `assert condition` but instead of marking the example as failed it marks it as bad, thus preventing fuzz tests from using it as a falsifying example.

```cairo
%lang starknet

@external
func test_function_that_takes_nonzero_argument{syscall_ptr : felt*, range_check_ptr}(value):
    %{ assume(ids.value != 0) %}

    # ...

    return ()
end
```
:::warning
This cheatcode is only available in [fuzz tests](TODO).
:::

:::tip
You should use `assume` only for narrow checks, as it can slow down the tests significantly due to the need of more specific inputs.
:::
