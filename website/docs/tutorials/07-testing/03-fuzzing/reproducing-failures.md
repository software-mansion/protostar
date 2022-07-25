# Reproducing failures

An important aspect of developing code with a fuzz testing suite, is how to reproduce failing test cases. 
As for now, Protostar provides one mean of achieving this.

## Reproducing a test run with seed

When a test suite with fuzz test is run, Protostar will print out a numeric seed of a pseudo-random number generator used as a source of generated examples:

```
TODO
```

You can then recreate that test suite run with the [`--seed` CLI flag](../../../cli-reference.md#--seed-string).
