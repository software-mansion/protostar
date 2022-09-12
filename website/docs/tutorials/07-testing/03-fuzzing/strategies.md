# Strategies

While a felt is a basis of all types in Cairo, its whole value space rarely matches what values are
acceptable in tested code (for example, when using range checks builtin).

Using the [`given`](../02-cheatcodes/given.md) cheatcode,
one can instruct Protostar how constrained or adjusted the value space of fuzzed inputs should be.
Such constraints are provided declaratively, by assigning _strategies_ to the input parameters.
A strategy is an object that is capable of generating next input examples in specific way,
and also is capable of other internal features, such as simplifying failing examples.

By default, Protostar applies the [`strategy.felts()`](#strategyfelts) strategy to all felt
parameters.

```cairo title="Example"
@external
func setup_integers() {
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    return ();
}

@external
func test_integers{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt) {
    assert_le(a, b);
    return ();
}
```

This document is a guide to what strategies are available for generating examples and how to build
them.
All core strategies are contained in the [`strategy`](../02-cheatcodes/strategy.md)
cheatcode-namespace.

## `strategy.felts`

```python
def felts(): ...
```

Explores all possible felt values.

## `strategy.integers`

```python
def integers(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
): ...
```

Generates integer values, possibly bounded to provided range.

Assuming real numbers comparison semantics,
if `min_value` is not `None` then all values will be greater than or equal to `min_value`,
and if `max_value` is not `None` then all values will be less than or equal to `max_value`.
When applied to field elements, the unbounded values may rarely overflow. 
