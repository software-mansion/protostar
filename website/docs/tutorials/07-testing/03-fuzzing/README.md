# Fuzzing

:::info
This feature is actively developed and many new additions will land in future Protostar releases.
:::

Protostar tests can take parameters which makes such tests to be run in a _fuzzing mode_.
In this mode, Protostar treats the test case parameters as a specification of the test case,
in the form of properties which it should satisfy,
and tests that these properties hold in a large number of randomly generated input data.

This technique is often called _property-based testing_.

## Example

Let's see how fuzzing works in Protostar, by writing a test for an abstract "safe":

TODO

## Interpreting results

In fuzzing mode, the test is executed many times, hence test summaries are slightly more extensive:

```
[PASS] TODO (TODO, TODO, TODO)
```

Each resource counter presents a summary of observed values across all test runs:
- `μ` is the mean value of a used resource,
- `Md` is the median value of this resource,
- `min` is the lowest value observed,
- `max` is the highest value observed.
