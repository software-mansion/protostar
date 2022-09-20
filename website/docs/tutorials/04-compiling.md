---
sidebar_label: Compilation
---

# Project compilation

In order to compile your project:

1. Specify contracts and their files in `protostar.toml`.
2. Run `protostar build`.

# Specifying contracts and their files

Protostar needs to know how to generate contracts from Cairo files. Each Cairo file that contains an [entrypoint](#entrypoint) should be included in the `"protostar.contracts"` section of the configuration file.

For example, the following configuration tells Protostar to generate two contracts — 'foo' and 'bar'.

```toml title="protostar.toml"
# ...

["protostar.contracts"]
foo = [
    "./src/main.cairo",
]
bar = [
    "./src/main.cairo",
]
```
### Entrypoint
An entrypoint is a function decorated with one of the following decorators:

- [`@constructor`](https://starknet.io/docs/hello_starknet/constructors.html)
- [`@external`](https://starknet.io/docs/hello_starknet/intro.html)
- [`@view`](https://starknet.io/docs/hello_starknet/intro.html)
- [`@l1_handler`](https://starknet.io/docs/hello_starknet/l1l2.html?highlight=l1_handler)





### Contract name
A contract name refers to an attribute name in this `“protostar.contracts”` section of the configuration file. You can use contract name as a reference to a contract in some Protostar features. In the example above, `foo` and `bar` are contract names.

# Compiling your project

Once you specified contract configurations, run:

```console
$ protostar build
```

```console title="A compilation result."
$ ls ./build
bar.json     bar_abi.json foo.json     foo_abi.json
```

:::note
Protostar detects account contracts. Unlike `starknet-compile`, you don't have to provide `--account_contract` flag to compile them.
:::

### Output directory

By default, Protostar uses a `build` directory as a compilation destination. However, you can specify a custom directory by running `build` command with the `--output` flag:

```console
protostar build --output out
```

### Cairo-lang version

Protostar ships with its own [cairo-lang](https://pypi.org/project/cairo-lang/) and [formatter](./08-formatting.md). You don't have to [set up the environment](https://www.cairo-lang.org/docs/quickstart.html). If you want to check what Cairo version Protostar uses to compile your project, run:

```text title="$ protostar -v"
Protostar version: 0.1.0
Cairo-lang version: 0.8.0
```

### Additional source directories

You can specify additional import search path by using `--cairo-path` flag.

```console
$ protostar build --cairo-path=modules cairo_libs
```
