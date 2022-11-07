# `skip`
```python
def skip(reason: Optional[str] = None) -> None:
```
Skip a test. You can use this cheatcode to prepare tests for functionality that isn't completed yet.

:::warning
This cheatcode is only available in [test case's setup](../README.md#setup-hooks).
:::

```cairo
%lang starknet

@external
func setup_function() {
    %{
        condition = True
        if condition:
            skip("Reason")
    %}
    return ();
}

@external
func test_function() {
    return ();
}
```
