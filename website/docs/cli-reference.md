# CLI Reference
## Generic flags
#### `--version`
Show Protostar and Cairo-lang version.
#### `--no-color`
Disable colors.
## Commands
### `init`
```shell
$ protostar init
```
Create a Protostar project.
#### `--existing`
Adapt current directory to a Protostar project.
### `build`
```shell
$ protostar build
```
Compile contracts.
#### `--cairo-path DIRECTORY[]`
Additional directories to look for sources.
#### `--disable-hint-validation`
Disable validation of hints when building the contracts.
#### `--output PATH`
An output directory that will be used to put the compiled contracts in.