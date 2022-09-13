# `max_examples`

```python
def max_examples(max_examples: int):
```

Sets the maximum number of examples to explore by the fuzzer.
Fuzzer tries at most this many input examples. If it does not find any failing, test will pass.

:::warning
This cheatcode is only available in [setup hooks](../README.md#setup-hooks).
:::

```cairo title="Example"
@external
func setup_integers() {
    %{ max_examples(20) %}
    return ();
}

@external
func test_integers{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    assert_le(a, b);
    return ();
}
```

Protostar defaults to 100 examples.
This default value is chosen to suit a workflow where the test will be part of a suite that
is regularly executed locally or on a CI server,
balancing total running time against the chance of missing a bug.

If you are just scratching tests for quick experimentation, not meant to be committed to source
repository, running tens of thousands of examples is quite reasonable as Protostar's fuzzer may miss
uncommon bugs with default settings.

This cheatcode has no effects on standard test cases.
