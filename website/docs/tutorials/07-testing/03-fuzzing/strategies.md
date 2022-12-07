# Strategies

Often in code we operate on some assumptions about the possible values of variables. 
For example we can perform greater than zero validation early in the code, and we can assume that variables are greater than zero in the subsequent code. 
Fuzzer allows to provide such assumptions to avoid testing against values which are not covered by the code. 

Cheatcode [`given`](../02-cheatcodes/given.md),
instructs the fuzzer to adopt a specific fuzzing strategy for input parameters.
Such strategies are provided declaratively, by assigning _strategies_ to the input parameters as on the example below.

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
def felts(*, rc_bound: bool = False) -> Strategy: ...
```

By default, explores all possible felt values.

If keyword argument `rc_bound` is `True`, explores felts which can be passed to the `range_check`
builtin.
This narrows the range of explored values according to the parameters of Cairo runtime.
Use this functionality, if fuzzed values will be passed to any of the `assert_*` functions from
`starkware.cairo.common.math` module.

### `strategy.integers`

```python
def integers(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> Strategy: ...
```

Generates integer values, possibly bounded by provided range.

```python title="Examples"
strategy.integers(0, 100)
strategy.integers(max_value=3000)
strategy.integers(11)
```

Fuzzer picks integers from provided range and then converts them to felts.
If `min_value` is not `None` then all values will be greater than or equal to `min_value`,
and if `max_value` is not `None` then all values will be less than or equal to `max_value`.

### `strategy.short_strings`
```python
def short_strings() -> Strategy:
```

Generates strings with ASCII characters of length that passes the condition `0 <= length <= 31`.

:::info
Max size `31` comes from [the docs](https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals).
:::

## Adapting strategies

Often it is the case that a strategy does not produce exactly what is desired and it is necessary to further
adapt the generated values.
Although this could be done in tests directly, this hurts because fuzzer does not know about the adaptation and may repeatedly test the same values.
The [`assume`] and [`reject`] cheatcodes provide simple interfaces to adapt an advanced strategy.
Those are not very good considering the performance.
Fuzzer can execute tests on rejected data anyway and will just ignore failure when it happens.

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

Rejects examples not matching a condition.

```python title="Example"
strategy.felts().filter(lambda x: x not in [3, 5, 8])
```

The outcome is similar to using the [`assume`] or [`reject`] cheatcodes, but `filter` does not
require executing tested Cairo function and thus is more performant.
Try to use `filter` only to avoid unwanted corner cases rather than attempting to cut out a large
portion of the searched input values.

Fuzzer draws random data from the original strategy and only afterwards checks if it passes filter conditions.
If too many variables are restricted, fuzzer will reject test execution.

### Combining

```python
def one_of(*strategies: Strategy) -> Strategy: ...
```

Returns a strategy which generates values from any of the argument strategies.

```python title="Example"
strategy.one_of(
    strategy.integers(0, 100),
    strategy.integers(1000, 1200),
)
```

[`assume`]: ../02-cheatcodes/assume.md

[`reject`]: ../02-cheatcodes/reject.md
