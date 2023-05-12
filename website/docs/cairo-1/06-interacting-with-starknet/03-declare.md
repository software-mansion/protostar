# Declaring new contracts

Starknet provides a distinction between contract class and instance. This is similar to difference between writing the
code of a `class MyClass {}` and creating a new instance of it `let myInstance = MyClass()` in object-oriented
programming languages.

To deploy new contract instance, you need to:

1. Declare a contract on the network
2. Deploy a instance of that declared contract

For detailed API description, see [declare-cairo1 command reference](../../cli-reference.md#declare-cairo1).

## Usage example

:::note
Building a contract before running `declare-cairo1` is not required. Protostar builds a contract during declaration under the hood.
under the hood.
:::

First make sure contract is defined in the `protostar.toml`:

```toml title=protostar.toml
# ...
[contracts]
my_contract = ["src"]
```

Then run:

```console title="protostar declare-cairo1 my_contract --network testnet"
Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...
```

:::info
The declare transaction must be signed and requires paying a fee, similarly to how invoke transaction does.
See [signing](./02-invoke.md#signing) for more details.
:::