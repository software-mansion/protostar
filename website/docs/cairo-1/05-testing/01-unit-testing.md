---
sidebar_label: Unit testing
---

# Unit testing
Protostar lets you test standalone cairo functions. This technique is referred to as unit testing. You should write as many unit tests as possible as these are **much faster** than [integration tests](./02-integration-testing.md).

## Writing your first test

First, add the following code to the `src/lib.cairo` file:
```
fn sum(a: felt252, b: felt252) -> felt252 {
    return a + b;
}
```

Now, let's test this function. Create a file `tests/test_sum.cairo`:
```
use your_project_name::sum;

#[test]
fn test_sum() {
    assert(sum(2, 3) == 5, 'sum incorrect');
}
```

Now run your test using this command:
```
protostar test-cairo1 ./tests
```

You should see something like this:
```
Collected 2 suites, and 3 test cases (10.64)
[PASS] tests/test_sum.cairo test_sum (time=0.00s)
Test suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Seed:        2752673895
17:20:43 [INFO] Execution time: 5.0 s
```

## Test collecting
Protostar collects all test suites specified under the path passed as an argument. You can pass either directory or a specific file. A test suite is every `.cairo` file with a name starting from `test_` or ending with `_test`. Protostar considers as a test case each function, inside a test suite, with `#[test]` attribute.

:::warning
Test cases cannot return any values and cannot take any arguments.
:::

## Failing tests

Your tests fail when code *panics*. To write a test that fails, you will need to use `panic` function, here's how you do it:

```
use array::ArrayTrait;

// Single value in the panic payload
#[test]
fn test_panic_single_value() {
    let mut data = ArrayTrait::new();
    data.append('this one should fail');
    panic(data)
}
```

Of course, if any of the functions you call from tests will *panic*, your test will fail as well.