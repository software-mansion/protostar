# Testing

Protostar provides a flexible testing environment for Cairo smart contracts.
It allows to write unit/integration tests with a help of [cheatcodes](02-cheatcodes/README.md).

## Unit testing
We will start with a [just created protostar project](../03-project-initialization.md).
In your `src` directory create a `utils.cairo` file
```cairo title="src/utils.cairo"
func sum_func{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) -> felt {
    return a + b;
}
```
This is our target function, which we are going to test.
Then in the `tests` directory create file `test_utils.cairo`, which contains a single test case.
```cairo title="tests/test_utils.cairo"
%lang starknet

from src.utils import sum_func

@external
func test_sum{syscall_ptr: felt*, range_check_ptr}() {
    let r = sum_func(4, 3);
    assert r = 7;
    return ();
}
```

Then run your test with
```shell
protostar test ./tests
```

:::info
In the example above, Protostar will run every test case it manages to find in the `tests` directory. You can read more about specifying where and how Protostar should search for test cases by running `protostar test --help`. 
:::

:::tip
If you experience any errors during test collection phase consider using `--safe-collecting` flag.
:::

```console title="Expected result"
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
    assert_eq,
    assert_not_eq,
    assert_signed_lt,
    assert_signed_le,
    assert_signed_gt,
    assert_unsigned_lt,
    assert_unsigned_le,
    assert_unsigned_gt,
    assert_signed_ge,
    assert_unsigned_ge,
)
```

:::info
If your IDE supports Cairo and doesn't know how to import `protostar`, add the following directory
`$(which protostar)/../cairo` to the [`CAIRO_PATH`](https://www.cairo-lang.org/docs/how_cairo_works/imports.html?highlight=cairo_path).
:::

You can find all [assert signatures here](https://github.com/software-mansion/protostar/blob/master/cairo/protostar/asserts.cairo).

## Setup hooks

Often while writing tests you have some setup work that needs to happen before tests run.
The `__setup__` ([setup suite](#setup-suite)) and `setup_<test_name>` ([setup case](#setup-case))
hooks can simplify and speed up your tests.

Use the `context` variable to pass data from setup hooks to test functions as demonstrated in
examples below.

### Setup suite

```cairo
@external
func __setup__()
```

The setup suite hook is shared between all test cases in a test suite (Cairo module),
and is executed before test cases.

```cairo title="Using setup suite hook"
@external
func __setup__() {
    %{ context.contract_a_address = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo").contract_address %}
    return ();
}

@external
func test_something() {
    tempvar contract_address;
    %{ ids.contract_address = context.contract_a_address %}

    // ...

    return ();
}
```

:::info
Protostar executes `__setup__` only once per test suite.
Then, for each test case Protostar copies the StarkNet state and the `context` object.
:::

### Setup case

```cairo
@external
func setup_tested_property()

@external
func test_tested_property()
```

The setup case hook is bound to a matching test case and is executed just before the test case
itself.
These hooks are executed with a context built by the `__setup__` hook, but in isolation for each
test separately, before jumping into test case function itself.
This makes them useful to extract test-specific setup logic from tested code itself.

```cairo title="Using setup case hook to prepare test-specific state"
@external
func __setup__{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    balance.write(10);
    return ();
}

@external
func setup_need_more_money{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    balance.write(10000);
    return ();
}

@external
func test_need_more_money{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    alloc_locals;
    let (amount_ref) = balance.read();
    local amount = amount_ref;

    assert amount = 10000;

    return ();
}

@external
func test_foo{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}() {
    alloc_locals;
    let (amount_ref) = balance.read();
    local amount = amount_ref;

    assert amount = 10;

    return ();
}
```

You can also use case hooks to configure the behavior of a particular test case,
for example, by calling the [`max_examples`] cheatcode.
Some configuration-specific cheatcodes are only available within setup cases, like [`example`]
and [`given`]:

```cairo title="Using setup case hook to configure fuzzing test"
@external
func setup_something() {
    %{
        max_examples(500)
        given(a = strategy.felts())
    %}
    return ();
}

@external
func test_something(a: felt) {
    // ...

    return ();
}
```

### Importing Python modules in hints

Protostar allows using external Python code in hint blocks, for example to verify a signature using third party library.

The `cairo-path` is automatically added to `sys.path` in executed hints. This includes project root, `src` and `lib` directories. Any Python module files stored there can be imported without any extra configuration.

The [`PYTHONPATH` environment variable ](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH) is fully supported, and Protostar will extend `sys.path` with this variable's value in executed Cairo code.
This approach can be used to include some packages from Python virtual environment (by adding `site_packages` to the `PYTHONPATH`).

For example, having the standard project file structure:

```
.
├── lib
├── protostar.toml
├── src
│   └── main.cairo
└── tests
    ├── pymodule.py
    └── test_main.cairo
```

In `pymodule.py`:

```python
def get_three():
    return 3
```

The `get_three` function can be used in `test_main.cairo` like this:

```cairo
%lang starknet
from src.main import balance, increase_balance
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_getting_tree() {
    alloc_locals;
    local res;
    %{
        from tests.pymodule import get_three
        ids.res = get_three()
    %}

    assert res = 3;
    return ();
}
```

[`example`]: ./02-cheatcodes/example.md
[`given`]: ./02-cheatcodes/given.md
[`max_examples`]: ./02-cheatcodes/max-examples.md
