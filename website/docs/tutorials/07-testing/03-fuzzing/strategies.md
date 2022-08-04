# Strategies

While a felt is a _lingua franca_ of Cairo runtime, its whole value space is rarely covered by
domain space in tested code.

Using the [`given`](../02-cheatcodes/given.md) cheatcode,
one can instruct Protostar how constrained or adjusted the value space of fuzzed inputs should be.

By default, Protostar applies the [`strategy.unsigned()`](#strategyunsigned) strategy to all felt
parameters.

```cairo title="Example"
@external
func test_integers{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    assert_le(a, b)
    return ()
end
```

This document is a guide to what strategies are available for generating data and how to build them.
All core strategies are contained in a [`strategy`](../02-cheatcodes/strategy.md)
cheatcode-namespace.

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

## `strategy.signed`

```python
def signed(): ...
```

Explores all felt values, by feeding Cairo VM values from `MIN_FELT` to `MAX_FELT`, where:
- `MIN_FELT = -FIELD_PRIME / 2`
- `MAX_FELT = FIELD_PRIME / 2`

## `strategy.unsigned`

```python
def unsigned(): ...
```

Explores all felt values, by feeding Cairo VM values from 0 to field prime used in computation.
