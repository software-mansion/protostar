# `reject`
```python
def reject() -> None:
```
`reject()` skips testing against the given example.

It is equivalent to `assume(False)`.

:::warning
This cheatcode is only available in [fuzz tests](../fuzzing).
:::

```cairo
%lang starknet

@external
func test_function_that_takes_nonzero_argument{syscall_ptr : felt*, range_check_ptr}(value):
    if value != 0:
        %{ reject() %}
        assert 0 = 0
    end

    # ...

    return ()
end
```

:::tip
You should use `reject` only for narrow checks, as it can slow down the tests significantly due to the need of more specific inputs.
:::