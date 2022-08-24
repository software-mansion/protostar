# Testing

Protostar provides a flexible testing environment for Cairo smart contracts.
It allows to write unit/integration tests with a help of [cheatcodes](02-cheatcodes/README.md).

## Unit testing
We will start with a [just created protostar project](../03-project-initialization.md).
In your `src` directory create a `utils.cairo` file
```code title="src/utils.cairo"
func sum_func{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt) -> (res : felt):
    return (a+b)
end
```
This is our target function, which we are going to test.
Then in the `tests` directory create file `test_utils.cairo`, which contains a single test case.
```code title="tests/test_utils.cairo"
%lang starknet

from src.utils import sum_func

@external
func test_sum{syscall_ptr : felt*, range_check_ptr}():
    let (r) = sum_func(4,3)
    assert r = 7
    return ()
end
```

Then run your test with
```
protostar test ./tests
```

:::info
In the example above, Protostar will run every test case it manages to find in the `tests` directory. You can read more about specifying where and how Protostar should search for test cases by running `protostar test --help`. 
:::

:::tip
If you experience any errors during test collection phase consider using `--safe-collecting` flag.
:::

```console title="expected result"
Collected 1 items

test_utils: .
----- TEST SUMMARY ------
1 passed
Ran 1 out of 1 total tests
```

:::info
You can place your test files anywhere you want. Protostar recursively searches 
the given directory for Cairo files with a name starting with `test_` and treats them as tests files. 
All functions inside a test file starting with `test_` are treated as separate test cases.
:::

:::warning
Protostar auto-removes constructors from test files. You can test a constructor using the `deploy_contract` cheatcode.
:::

## Asserts

Protostar ships with its own assert functions. They don't accept [implicit arguments](https://www.cairo-lang.org/docs/how_cairo_works/builtins.html?highlight=implicit%20arguments#implicit-arguments) compared to asserts from [`starkware.cairo.common.math`](https://github.com/starkware-libs/cairo-lang/blob/master/src/starkware/cairo/common/math.cairo). You can import Protostar asserts in the following way:

```cairo title="test_my_contract.cairo"
from protostar.asserts import (
    assert_eq, assert_not_eq, assert_signed_lt, assert_signed_le, assert_signed_gt,
    assert_unsigned_lt, assert_unsigned_le, assert_unsigned_gt, assert_signed_ge,
    assert_unsigned_ge)
```

:::info
If your IDE supports Cairo and doesn't know how to import `protostar`, add the following directory
`$(which protostar)/../cairo` to the [`CAIRO_PATH`](https://www.cairo-lang.org/docs/how_cairo_works/imports.html?highlight=cairo_path).
:::

You can find all [assert signatures here](https://github.com/software-mansion/protostar/blob/master/cairo/protostar/asserts.cairo).

## Setup hooks

Often while writing tests you have some setup work that needs to happen before tests run.
The `__setup__` and `setup_*` hooks can simplify and speed up your tests.

1. The `__setup__` hook is shared between all test cases in module, and is executed before
   test case.
2. The `setup_*` case hook is bound to a matching `test_*` case and is executed between
   the `__setup__` hook and the test case.
   Use case hooks to configure the behavior of particular test case,
   for example, by calling the [`max_examples`](./02-cheatcodes/max-examples.md) cheatcode.

Use `context` variable to pass data from setup hooks to test functions as demonstrated in
examples below:

```cairo title="Using __setup__ hook"
%lang starknet

@external
func __setup__():
    %{ context.contract_a_address = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo").contract_address %}
    return ()
end

@external
func test_something():
    tempvar contract_address
    %{ ids.contract_address = context.contract_a_address %}

    # ...

    return ()
end
```

```cairo title="Using setup_* case hook"
%lang starknet

@external
func setup_test_something():
    %{ max_examples(500) %}
    return ()
end

@external
func test_something(a : felt):
    # ...

    return ()
end
```

:::info
Protostar executes `__setup__` only once per
[test suite](https://en.wikipedia.org/wiki/Test_suite).
Then, for each test case Protostar copies the StarkNet state and `context` object.
:::
