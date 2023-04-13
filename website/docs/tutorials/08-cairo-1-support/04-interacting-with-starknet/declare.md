# Declaring new contracts

Starknet provides a distinction between contract class and instance. To deploy new contract instance, you need to:

1. Ensure correct path to the contract is defined in `protostar.toml`'s \[contract\] section.
2. Declare a contract on the network
3. Deploy an instance of that contract

For detailed API description, see [declare command reference](../../../cli-reference.md#declare-cairo1).

## Usage example

To declare a contract from the Protostar CLI you need to build your project and use the `protostar declare-cairo1`
command.

First make sure contract is defined in the `protostar.toml`:

```toml title=protostar.toml
# ...
[contracts]
my_contract = ["src"]
```

Then run:

```console title="protostar declare my_contract --network testnet"
Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...
```
