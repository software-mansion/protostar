---
sidebar_label: Compilation (1 min)
---

# Project compilation
In order to compile your project:
1. Specify main files in `protostar.toml`.
2. Run `protostar build`.

# Specifying main files
Protostar needs to know which Cairo files should be treated as contracts. Your Protostar project may consist of multiple contracts, which share common code. You can specify contract files in the `protostar.toml`.
```toml title="Key 'main' accepts a list of relative paths to your main contract files."
["protostar.contracts"]
main = [
    "./src/main.cairo",
]
```
# Compiling your project
Once you specified your main files, run:
```console
$ protostar build
```

```console title="A compilation result."
$ ls ./build
main.json     main_abi.json
```

### Output directory
By default, Protostar uses a `build` directory as a compilation destination. However, you can specify custom directory by running `build` command with the `--output` flag:
```console
protostar build --output out
```

### Cairo-lang version
Protostar ships with its own [cairo-lang](https://pypi.org/project/cairo-lang/). You don't have to [set up the environment](https://www.cairo-lang.org/docs/quickstart.html). If you want to check what Cairo version Protostar uses to compile your project, run:
```cairo
$ protostar -v
Protostar version: 0.1.0
Cairo-lang version: 0.8.0
```

### Additional source directories
You can specify additional import search path by using `--cairo-path` flag.

```console
$ protostar build --cairo-path=modules cairo_libs
```

