# Understanding Cairo Packages

There are several requirements that Cairo packages have to follow. Further documentation pages assume some knowledge
of the Cairo package structure. Please refer to this page for details.

## `.cairo` files

Files with the `.cairo` extension contain Cairo code, including Starknet contracts. A file may define multiple methods,
structures etc.

## Modules

A module consists of one or more Cairo files, usually organized in a single directory. To define a module, create a `.cairo`
file named like the module and define components of this module with the `mod` keyword.

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

Package is a collection of modules that also defines `cairo_project.toml` and `lib.cairo` files.

:::info
Some other tools use name "crates" for packages.
:::

### `cairo_project.toml`

It is needed for the definition of `[crate_roots]`, which is a directory containing `lib.cairo`.

The default `cairo_project.toml` file contains only the definition of the `hello_starknet` package which is contained in
the `src` directory.

It is good practice for the package name defined here to match the top-level directory name.

As an example we can define:
```toml title="cairo_project.toml"
[crate_roots]
hello_starknet = "src"

### `lib.cairo`

It is the root of the package tree. Here you can define functions, declare used modules, etc.

The default one has `contracts` and `business_logic` module declarations:

```cairo title="lib.cairo"
mod business_logic;
mod contracts;
```

### Creating and using a new modules

Suppose we wanted to create a module called `mod1` inside the `hello_starknet` package and use it in tests.
We want this module to only have one file `functions.cairo` containing one function defined like:

```cairo title="functions.cairo"
fn returns_three() -> felt252 {
    3
}
```

Here is our initial file structure

```
my_project/
└── hello_starknet/
    ├── src/
    │   ├── business_logic/
    │   │   └── utils.cairo
    │   ├── contracts/
    │   │   └── hello_starknet.cairo
    │   ├── business_logic.cairo
    │   ├── contracts.cairo
    │   └── lib.cairo
    └── cairo_project.toml
```

#### Adding a new module

Here are the steps we need to take:

1. Create a `mod1` subdirectory inside `src`.
2. Create file `functions.cairo` inside `mod1` subdirectory and define your code there
3. Create `mod1.cairo` file **in the `src` directory**, with the contents of

```cairo title="mod.cairo"
mod functions;
```

4. Update the `lib.cairo` file to include `mod1`. It's contents should now look like this

```cairo title="lib.cairo"
// previous code stays
// ...
mod mod1;
```

If you followed the steps correctly, your new project structure should look like this

```
my_project/
└── hello_starknet/
    ├── src/
    │   ├── business_logic/
    │   │   └── utils.cairo
    │   ├── contracts/
    │   │   └── hello_starknet.cairo
    │   ├── mod1/  <------------------- new directory
    │   │   └── functions.cairo  <----- new file
    │   ├── business_logic.cairo
    │   ├── contracts.cairo
    │   ├── lib.cairo  <--------------- contents updated
    │   └── mod1.cairo  <-------------- new file
    └── cairo_project.toml
```

#### Using added module

You now use your function in the HelloStarknet contract use `hello_starknet::mod1::functions::returns_three()`.

## Packages and modules names considerations

The names must use only ASCII alphanumeric characters or `_`, and cannot be empty. It cannot also start with an underscore.