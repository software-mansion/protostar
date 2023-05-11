# Understanding Cairo packages

There are several requirements that Cairo packages have to follow. These are explained in the following sections.

You can refer to [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference) for
more details.

## Modules

A module consists of one or more Cairo files, usually organized in a single directory. To define a module, create
a `.cairo`
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

Package consist of multiple modules and must define `cairo_project.toml` and `lib.cairo` files.

:::info
Some other tools and resources,
including [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference), use the
term "crates" for packages.
:::

### `cairo_project.toml`

It is a required part of the package definition. It contains `[crate_roots]` parameter, which is the path to
the `lib.cairo` file.

It is good practice for the package name defined here to match the top-level directory name.

As an example we can define:

```toml title="cairo_project.toml"
[crate_roots]
my_package = "src"
```

### `lib.cairo`

It is the root of the package tree. Here you can define functions, declare used modules, etc.

```cairo title="lib.cairo"
mod my_module;
mod my_other_module;
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
    │   └── lib.cairo
    └── cairo_project.toml
```

#### Adding a new module

Here are the steps we need to take:

1. Create a `mod1` subdirectory inside `src`.
2. Create file `functions.cairo` inside `mod1` subdirectory and define your code there
3. Create `mod1.cairo` file **in the `src` directory**, with the contents of

```cairo title="mod1.cairo"
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
    │   ├── mod1/  <------------------- new directory
    │   │   └── functions.cairo  <----- new file
    │   ├── lib.cairo  <--------------- contents updated
    │   └── mod1.cairo
    └── cairo_project.toml
```

#### Using added module

You now use your function with `hello_starknet::mod1::functions::returns_three()`.

## Packages and modules names considerations

The name must be a valid Cairo identifier which means:
- it must use only ASCII alphanumeric characters or underscores 
- it cannot start with a digit
- it cannot be empty
- it cannot be a valid Cairo keyword or a single underscore (`_`).