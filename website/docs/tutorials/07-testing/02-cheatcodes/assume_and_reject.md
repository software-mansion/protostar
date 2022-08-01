# `assume and reject`
Those two cheatcodes can be used **only** in fuzz tests.

### `assume`
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
<br/>

### `reject`
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
<br/>

:::tip
You should use `reject` and `assume` only for narrow checks, as they can slow down the tests significantly due to the need of more specific inputs.
:::