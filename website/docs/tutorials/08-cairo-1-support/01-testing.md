---
sidebar_label: Testing
---

# Running tests with Cairo 1

:::info
This functionality is in the alpha stage, expect rapid iteration
:::


## Writing your first test

To make a test function, you need to mark the function with a decorator `#[test]`

```
#[test]
fn test_bool_operators() {
    assert(1 == 1);
}
```

To write a test that fails, you will need to use `panic`, here's how you do it:

```
use array::ArrayTrait;

// Single value in the panic payload
#[test]
fn test_panic_single_value() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, 21);
    panic(data)
}

// Multiple values in the panic payload
#[test]
fn test_panic_multiple_values() {
    let mut data = array_new::();
    array_append::(ref data, 101);
    array_append::(ref data, 102);
    array_append::(ref data, 103);
    panic(data)
}
```

## Running the tests

To run cairo 1 tests, there is a special command called `test-cairo1`.
It is a sibling command to the `test` command, it will collect all the tests in the given directory/module, run them, and print out a summary.

Tests are run on Cairo VM, so no Starknet syscalls are available from the test code.

:::info
There is no support currently for starknet contracts at the moment, it's a work in progress.
:::

## Caveats
### 1. Test collecting
`test-cairo1` will collect all tests ending with `.cairo` since there's no distinction between cairo 0 and cairo 1 files in terms of extension right now.

That means that you will either have to specify a regex to match your test names (see [command reference](../../cli-reference.md#test-cairo1)), or keep them in a separate directory to avoid syntax errors.

A `test_` file prefix or `_test` postfix is required as well, to mark the files as test suites.

### 2. Test state

`__setup__` and `<test_name>_setup` from the previous version are not supported for now.

### 3. Test function type

A test function must not return any values, be panickable, and not have any arguments for correct test result assessment

In case last statement in function returns a value, you can add a line with a `;` in order to avoid returning any values from the test function.

Example:
```
fn foo() -> felt {
    1
}

#[test]
fn test_foo() {
    foo();
    ; // foo returns a value, so this would make the test invalid 
}
```


If you fail to comply to those rules, the test function will not pass the type check, and test collecting will fail.
