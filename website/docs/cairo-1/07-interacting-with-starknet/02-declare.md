# Declaring new contracts

Starknet provides a distinction between contract class and instance. This is similar to difference between writing the
code of a `class MyClass {}` and creating a new instance of it `let myInstance = MyClass()` in object-oriented
programming languages.

To deploy a new contract, for instance, you need to:

1. Declare a contract on the network
2. Deploy an instance of that declared contract

For detailed API description, see [declare command reference](../../cli-reference.md#declare).

## Usage example

:::note
Building a contract before running `declare` is not required. Protostar builds a contract during declaration under the hood.
:::

First make sure contract is defined in the [`protostar.toml`](../05-protostar-toml.md):

```toml title=protostar.toml
# ...
[contracts]
my_contract = ["src"]
```

Then run:

```shell title="Example"
protostar declare my_contract \
  --network testnet \
  --account-address 0x0481Eed2e02b1ff19Fd32429801f28a59DEa630d81189E39c80F2F60139b381a \
  --max-fee auto \
  --private-key-path ./.pkey
Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...
```

:::info
The declare transaction must be signed and requires paying a fee, similarly to how invoke transaction does.
See [signing](./01-invoke.md#signing) for more details.
:::
