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

## Core strategies

All core strategies are contained in the [`strategy`](../02-cheatcodes/strategy.md)
cheatcode-namespace.

### `strategy.felts`

```python
def felts() -> Strategy: ...
```

Explores all possible felt values.

### `strategy.integers`

```python
def integers(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> Strategy: ...
```

Generates integer values, possibly bounded to provided range.

Assuming real numbers comparison semantics,
if `min_value` is not `None` then all values will be greater than or equal to `min_value`,
and if `max_value` is not `None` then all values will be less than or equal to `max_value`.
When applied to field elements, the unbounded values may rarely overflow.

```python title="Examples"
strategy.integers(0, 100)
strategy.integers(max_value=3000)
strategy.integers(11)
```

## Adapting strategies

Often it is the case that a strategy does not produce exactly what is desired and a need to further
adapt the generated values arise.
Although this could be done in tests directly, this hurts because adaptation may waste fuzzing
cycles (by repeatedly testing same values after adaptation) and the code has to be copied in every
test.
There are also the [`assume`] and [`reject`] cheatcodes, but this should only be used to discard
only few unwanted inputs.

Protostar provides ways to build strategies by transforming other ones.

### Mapping

```python
class Strategy:
    def map(self, mapping_function: Callable[[int], int]) -> Strategy: ...
```

Applies provided mapping function to all searched inputs values.

```python title="Example"
strategy.felts().map(lambda x: x // 2)
```

### Filtering

```python
class Strategy:
    def filter(self, filter_function: Callable[[int], bool]) -> Strategy: ...
```

Allows rejecting examples matching a condition.

The outcome is similar to using the [`assume`] or [`reject`] cheatcodes, but `filter` does not
require executing tested Cairo function and thus is more performant.
Try to use `filter` only to avoid unwanted corner cases rather than attempting to cut out a large
portion of the searched input values.

The `filter` method is not magic and hard to satisfy conditions may cause the fuzzer to fail.

```python title="Example"
strategy.felts().filter(lambda x: x not in [3, 5, 8])
```

### Combining

```python
def one_of(*strategies: Strategy) -> Strategy: ...
```

Return a strategy which generates values from any of the argument strategies.

```python title="Example"
strategy.one_of(
    strategy.integers(0, 100),
    strategy.integers(1000, 1200),
)
```

[`assume`]: ../02-cheatcodes/assume.md

[`reject`]: ../02-cheatcodes/reject.md
