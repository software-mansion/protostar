---
sidebar_label: protostar.toml V2
---
# `protostar.toml` V2


```toml
[project]
protostar-version = "PROTOSTAR_VERSION"

[contracts]
main = ["src/feature_a.cairo", "src/feature_b.cairo"]
proxy = ["src/proxy.cairo"]
account = ["src/account.cairo"]
```





## Migrating from `protostar.toml` V1
In order to migrate your protostar.toml V1, run:
```
protostar migrate-configuration-file
```

### Changes
- removed `protostar` prefix from configuration sections
- section names cannot be in double quotes
- merged `["protostar.config"]` and `["protostar.shared_command_configs"]` sections into the project section
- `snake_case` is no longer supported (use `kebab-case` everywhere)


| protostar.toml V1                                    | protostar.toml V2            |
| ---------------------------------------------------- | ---------------------------- |
| `["protostar.config"]`                               | `[project]`                  |
| `["protostar.project"]`                              | `[project]`                  |
| `["protostar.shared_command_configs"]`               | `[project]`                  |
| `["protostar.contracts"]`, `["protostar.<COMMAND>"]` | `[contracts]`, `[<COMMAND>]` |
| `cairo_path = ...`, `cairo-path = ...`               | `cairo-path = ...`           |

