# Dependencies

Protostar manages dependencies using [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) ([similarly to Foundry](https://onbjerg.github.io/foundry-book/projects/dependencies.html)). This is the reason why Protostar expects [git](https://git-scm.com/) to be installed. Keep this in mind, especially if your project uses git submodules.

:::note
Using Git submodules for package management is not ideal approach. Therefore, [Starkware](https://starkware.co/) plans to create [proper package manager](https://starkware.notion.site/Cairo-Package-Manager-similar-to-Rust-Crate-e3f668cde90c4996afbd8af4b42bd9bf).
:::

## Adding a dependency

To add a dependency, run `protostar install` from working directory of your project:

```sh
$ protostar install https://github.com/bellissimogiorno/cairo-integer-types
12:00:00 [INFO] Installing cairo_integer_types (https://github.com/bellissimogiorno/cairo-integer-types)

$ tree -L 2
.
├── lib
│   └── cairo_integer_types
├── protostar.toml
├── src
│   └── main.cairo
└── tests
    └── test_main.cairo

4 directories, 3 files
```

### Alias

## Updating dependency

## Removing dependency
