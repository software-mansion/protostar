# Understanding Cairo packages

There are several requirements that Cairo packages have to follow. These are explained in the following sections.

You can refer to [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference) for
more details. 

Keep in mind that Protostar does not support `cairo_project.toml`. 
It uses [Scarb](https://docs.swmansion.com/scarb) and its [manifest files](https://docs.swmansion.com/scarb/docs/reference/manifest) instead.

## Dependencies management

Protostar uses [Scarb](https://docs.swmansion.com/scarb) and its [manifest files](https://docs.swmansion.com/scarb/docs/reference/manifest) to manage dependencies in your project.
In order to use Protostar with Cairo 1, you must have Scarb executable added to the `PATH` environment variable. 
The `PATH` variable is a list of directories that your system searches for executables.

To learn how to manage dependencies with Scarb, check [the documentation](https://docs.swmansion.com/scarb/docs/reference/specifying-dependencies).

:::info 
The name of your package is always the value
of the `name` key in the `[package]` section of your `Scarb.toml`. 
:::

## Modules

A module consists of one or more Cairo files, usually organized in a single directory. To define a module, create
a `.cairo` file named like the module and define components of this module with the `mod` keyword.

```
my_module/
├── a.cairo
├── b.cairo
└── c.cairo
my_module.cairo
```

```cairo title="my_module.cairo"
mod a;
mod b;
mod c;
```

Alternatively, modules can be defined within a file using

```cairo title="my_module.cairo"
mod my_module {
    fn function_a() -> ();
    // ...
}
```

## Packages

Package consist of multiple modules and must define `Scarb.toml` and `src/lib.cairo` files.

:::info
Some other tools and resources,
including [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference), use the
term "crates" for packages.
:::

### `Scarb.toml`

It is a [Scarb's manifest files](https://docs.swmansion.com/scarb/docs/reference/manifest) 
containing dependencies for your package.

Example content of this file:

```toml title="Scarb.toml"
[package]
name = "my_package"
version = "0.1.0"

[dependencies]
```

### `lib.cairo`

It is the root of the package tree, and it ***must*** be placed inside `src` folder. 
Here you can define functions, declare used modules, etc.

```cairo title="lib.cairo"
mod my_module;
mod my_other_module;
```

### Package with multiple modules

The module system in Cairo is inspired by 
[Rust's](https://doc.rust-lang.org/rust-by-example/mod/split.html) one. 
An example package with multiple modules:

```
my_project/
├── src/
│   ├── mod1/
│   │   └── functions.cairo
│   ├── mod1.cairo
│   ├── utils.cairo
│   └── lib.cairo
└── Scarb.toml
```

```cairo title="lib.cairo"
mod mod1;
mod utils;
```

```cairo title="mod1.cairo"
mod functions;
```

```cairo title="utils.cairo"
fn returns_two() -> felt252 {
    2
}
```

```cairo title="mod1/functions.cairo"
fn returns_three() -> felt252 {
    3
}
```

You can now use the defined functions with
`my_package::mod1::functions::returns_three()` and `my_package::utils::returns_two()`.

## Project with multiple contracts

Due to limitations of the Cairo 1 compiler, having multiple contracts defined in the package will cause
the `protostar build` command and other commands to fail.

**That is, having projects structured like this is not valid and will not work correctly.**

### Multi-contract project structure

Each contract must be defined in the separate package: a different directory with separate `Scarb.toml`
and `src/lib.cairo` files defined.

```
my_project/
├── package1/
│   ├── src/
│   │   ├── contract/
│   │   │   └── hello_starknet.cairo
│   │  ...
│   │   ├── contract.cairo
│   │   └── lib.cairo
│   └── Scarb.toml
├── package2/
│   ├── src/
│   │   ├── contract/
│   │   │   └── other_contract.cairo
│   │  ...
│   │   ├── contract.cairo
│   │   └── lib.cairo
│   └── Scarb.toml
...
├── src/
│   └── lib.cairo
├── Scarb.toml
└── protostar.toml
```

:::caution
Notice that the whole project itself is a package too.
This is due to the fact that [Scarb](https://docs.swmansion.com/scarb/)
does not support workspaces yet. If you do not need to include any code 
in the top level package, just leave the `my_project/src/lib.cairo` file empty.
:::

Define each contract in the `[contracts]` section of the protostar.toml.
```toml title="protostar.toml"
# ...
[contracts]
hello_starknet = ["package1/src"]
other_contract = ["package2/src"]
```

Remember to include the packages as [dependencies](https://docs.swmansion.com/scarb/docs/reference/specifying-dependencies) in `my_project/Scarb.toml`.
```toml title="my_project/Scarb.toml"
[package]
name = "my_package"
version = "0.1.0"

[dependencies]
package1 = { path = "package1" }
package2 = { path = "package2" }
```

### Testing multi-contract projects

For example, to test function `returns_two` defined in the `package1/business_logic/utils.cairo` write

```cairo title="my_project/test_package1.cairo"
#[test]
fn test_returns_two() {
    assert(package1::business_logic::utils::returns_two() == 2, 'Should return 2');
}
```

Or using the `use path::to::mod` syntax

```cairo title="my_project/test_package2.cairo"
use package1::business_logic::utils::returns_two;

#[test]
fn test_returns_two() {
    assert(returns_two() == 2, 'Should return 2');
}
```

Make sure that the `path::to::the::module` is correct for your package structure.

For more details on how to test contracts, see [this page](./06-testing/README.md).


## Packages and modules names considerations

The name must be a valid Cairo identifier which means:
- it must use only ASCII alphanumeric characters or underscores
- it cannot start with a digit
- it cannot be empty
- it cannot be a valid Cairo keyword or a single underscore (`_`)
