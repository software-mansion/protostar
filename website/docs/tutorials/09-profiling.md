# Profiling

## Prerequisites

You need pprof installed to interpret profiling results.
You can learn how to install it [in pprof documentation](https://github.com/google/pprof#building-pprof).

## How to profile a contract?

Protostar can help you diagnose which functions are the most expensive in terms of used resources.
Protostar currently measures:
- number of steps
- memory holes

If you want to generate profile for a test case, run:

```shell
protostar test --profiling test/test_file.cairo::test_case_name 
```
:::warning
You can only run profiling for a single test case.
:::

Protostar will run the test in the profiling mode (it may take a little more than ususal) and produce a file `profile.pb.gz`

Then you can read the profile using: 
```shell
go tool pprof -http=":8000" profile.pb.gz
```
### Example results

![Profiler](.prof1.jpg)
![Profiler](.prof2.jpg)
![Profiler](.prof3.jpg)
