---
sidebar_label: Unit testing
---

# Unit testing


## Writing your first test (TODO test if the example works)

First, add to the file `src/lib.cairo` following code:
```
fn sum(a: felt252, b: felt252) -> felt252 {
    return a + b;
}
```

Now, let's test this function. Create a file `tests/test_sum.cairo`:
```
use your_project_name::sum

#[test]
fn test_sum() {
    assert(sum(2, 3) == 5, 'sum incorrect');
}
```

Now run your test using command:
```
protostar test-cairo1 ./tests
```

You should see something like this:
```
Collected 2 suites, and 3 test cases (10.64)
[PASS] tests/test_sum.cairo Then (time=0.00s)
Test suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Seed:        2752673895
17:20:43 [INFO] Execution time: 5.0 s
```

## Test collecting
Protostar collects all test suites specified under the path passed as an argument. You can pass either directory or a specific file. Test suite is every `.cairo` file with name starting from `test_` or ending with `_test`. Protostar considers each function, inside a test suite, with `#[test]` attribute as a test case.

:::warning
Test cases cannot return any values, cannot take any arguments.
:::

## Failing tests (TODO test if the example works and fix the array syntax)

Your tests fails when code *panics*. To write a test that fails, you will need to use `panic` function, here's how you do it:

```
use array::ArrayTrait;

// Single value in the panic payload
#[test]
fn test_panic_single_value() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, `this one should fail`);
    panic(data)
}
```