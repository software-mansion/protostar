# Understanding Cairo packages

There are several requirements that Cairo packages have to follow. These are explained in the following sections.

You can refer to [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference) for
more details. 

Keep in mind that Protostar does not use `cairo_project.toml`. 
It uses [Scarb](https://docs.swmansion.com/scarb) - a powerful package manager -  and its [manifest files](https://docs.swmansion.com/scarb/docs/reference/manifest) instead.

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

Package consist of multiple modules and must define `Scarb.toml` and `src/lib.cairo` files.

:::info
Some other tools and resources,
including [official Cairo documentation](https://github.com/starkware-libs/cairo/tree/main/docs/reference), use the
term "crates" for packages.
:::

### `Scarb.toml`

It is a [Scarb's manifest files](https://docs.swmansion.com/scarb/docs/reference/manifest) used by Protostar to manage your dependencies with the help of Scarb.
This way you can manage your [dependencies](https://docs.swmansion.com/scarb/docs/reference/specifying-dependencies) as if you were using Scarb directly - you will not notice any difference!

Example content of this file:

```toml title="Scarb.toml"
[package]
name = "my_package"
version = "0.1.0"

[dependencies]
```

### `lib.cairo`

It is the root of the package tree and ***must*** be placed inside `src` folder. Here you can define functions, declare used modules, etc.

```cairo title="lib.cairo"
mod my_module;
mod my_other_module;
```

### Creating and using new modules

Suppose we wanted to create a module called `mod1` inside the `my_package` package and use it in tests.
We want this module to only have one file `functions.cairo` containing one function defined like:

```cairo title="functions.cairo"
fn returns_three() -> felt252 {
    3
}
```

Here is our initial file structure:

```
my_project/
├── src/
│   └── lib.cairo
└── Scarb.toml
```

#### Adding a new module

Here are the steps we need to take:

1. Create a `mod1` subdirectory inside `src`.
2. Create file `functions.cairo` inside `mod1` subdirectory and define your code there.
3. Create `mod1.cairo` file **in the `src` directory**, with the contents of

```cairo title="mod1.cairo"
mod functions;
```

4. Update the `lib.cairo` file to include `mod1`. It's contents should now look like this:

```cairo title="lib.cairo"
// previous code stays
// ...
mod mod1;
```

If you followed the steps correctly, your new project structure should look like this:

```
my_project/
├── src/
│   ├── mod1/  <------------------- new directory
│   │   └── functions.cairo  <----- new file
│   ├── lib.cairo  <--------------- contents updated
│   └── mod1.cairo <--------------- new file
└── Scarb.toml
```

#### Using the added module

You can now use your function with `my_package::mod1::functions::returns_three()`.

:::info
The name `my_package` is the value of the `name` key in the `[package]` section of your `Scarb.toml`.
:::

## Packages and modules names considerations

The name must be a valid Cairo identifier which means:
- it must use only ASCII alphanumeric characters or underscores
- it cannot start with a digit
- it cannot be empty
- it cannot be a valid Cairo keyword or a single underscore (`_`)
