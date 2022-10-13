---
sidebar_label: Profiling
---

# Profiling

## Prerequisites

You need pprof installed beforehand. You can learn how to install it [HERE](https://github.com/google/pprof#building-pprof)

## How to profile a contract?

In case you have a test with high number of steps/memory holes, Protostar can help you diagnose which functions are the most expansive in terms of those resources.

If you want to generate profile for a test case, run:

```shell
protostar test --profiling test/test_file.cairo::test_case_name 
```
:::warning
You can only run profiling for a single test case
:::

Protostar will run the test in the profiling mode (it may take a little more than ususal) and produce a file `profile.pb.gz`

Then you can read the profile using: 
```shell
go tool pprof -http=":8000" profile.pb.gz
```




