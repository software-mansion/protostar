---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project
To create a new Protostar project with cairo1 support, you will need to run the `protostar init-cairo1` command followed by the name of your project. For example:

```shell
protostar init-cairo1 my-project
```

After running the command, the following structure will be generated:

```
my-project/
├── src/
│   └── main.cairo
│   └── lib.cairo
│   └── cairo_project.toml
├── tests/
│   └── test_main.cairo
└── protostar.toml
```

This template contains:

- `src` directory
    - `cairo_project.toml` which is needed for compilation 
    - `main.cairo` file with one function definition
    - `lib.cairo` file which defines the module
- `test` directory
    - Single test file with one test for function defined in `main.cairo`
- `protostar.toml` containing information about the project

:::warning
This template will be changed in future versions, but the old one will still be usable with newer protostar versions
:::

## Cairo 1 modules

In order to understand how to create Cairo 1.0 modules, we need to talk about the purpose of `cairo_project.toml` and `lib.cairo`.
### Project defaults
#### 1. `cairo_project.toml`
It is needed for the definition of crate roots, which are the places where `lib.cairo` files are located.

The default `cairo_project.toml` file contains only the definition of the `src` crate 
```toml
[crate_roots]
src = "."
```

The `src` crate is then imported in our tests in following manner:
```
use src::main::fib;
```

:::warning
If you edit crate name in `cairo_project.toml`, make sure to reflect the changes in `linked-libraries` entry in `protostar.toml` as well
:::

#### 2. `lib.cairo`
It is the root of the module tree of the package. Here you can define functions, declare used modules, etc.

The default one has only the `main` module declaration:
```
mod main;
```
### Creating and using a new module

Suppose we wanted to create a module called `mod1` inside the `src` crate and use it in tests.

Here are the steps we need to take:

1. Create a `mod1` directory in the `src` crate
2. Create `mod1.cairo` alongside this directory. 
3. Create your source file inside of `mod1` (i.e. `functions.cairo` or any suitable name). Define your code here.
4. Declare the source file/files in `mod1.cairo`. The file contents should look like this (assuming you have `functions.cairo` from the previous step):
```
mod functions;
```
5. Declare the module in the root of the module tree - `lib.cairo`. After adding, the file contents should look like this:
```
mod main;
mod mod1;
```
6. You can import the symbols from `functions.cairo` in tests. For example, in `test_main.cairo`:
```
use src::mod1::functions::three;

#[test]
fn test_numbers() {
    assert(3 == three(), 'three() == 3');
}
```

## The protostar.toml
Apart from the usual things you can find in `protostar.toml`, there is a `linked-libarires` entry which is used to find cairo 1 modules in tests and building.
This makes it possible for you to include other modules from your dependencies if they are correct cairo 1 modules (with their own module definition and `cairo_project.toml`).

```
[project]
protostar-version = "0.9.2"
lib-path = "lib"
linked-libraries = ["src"]

[contracts]
```

:::warning
`[contracts]` section is not usable right now, since protostar can't build cairo 1 contracts yet 
:::