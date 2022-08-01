# `reject`
```python
def reject() -> None:
```
`reject()` is equivalent to `assume(False)`.

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
:::warning
This cheatcode is only available in [fuzz tests](TODO).
:::

:::tip
You should use `reject` only for narrow checks, as it can slow down the tests significantly due to the need of more specific inputs.
:::