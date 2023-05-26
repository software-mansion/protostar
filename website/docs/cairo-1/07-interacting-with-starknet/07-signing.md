# Signing

Protostar offers two ways of providing the signature:

## Default signer

By default, Protostar uses
the [StarkCurveSigner class](https://github.com/software-mansion/starknet.py/blob/68df1709c4f7664e317f5c5dbff5e9c220d11727/starknet_py/net/signer/stark_curve_signer.py#L36)
from Starknet.py to sign transactions.

The way of signing used by this class requires providing a private key (for signing) and account contract's address (to
fetch the nonce).
Depending on what account you use, these can be obtained in different ways. Refer to your account documentation for more
details.

### Providing account details in Protostar commands

To provide your account details when running Protostar commands, these arguments should be used

- `--private-key-path` - a path to the file containing private key, either in hex (prefixed with '0x') or decimal
  format.
- `--account-address` - your account contract's address on the appropriate network, either in hex (prefixed with '0x')
  or decimal
  format.

If you prefer not to store private key in a file, define a `PROTOSTAR_ACCOUNT_PRIVATE_KEY`
environment variable. Protostar will use that variable for the private key automatically when running commands.

## Using a custom signer class

If your account contract requires a different way of signing, you can create a custom signer class which inherits
from [BaseSigner](https://github.com/software-mansion/starknet.py/blob/68df1709c4f7664e317f5c5dbff5e9c220d11727/starknet_py/net/signer/base_signer.py#L8)
abstract class if 

To use a custom signer, provide a `--signer-class` argument when executing Protostar commands.

:::caution
The custom signer class must not take any arguments in the constructor, since we don't pass any args on instantiation.
:::

The Python file containing this class can be put next to Cairo source code.
Protostar synchronizes `PYTHONPATH` with project's `cairo_path`.
Modules that are dependencies of Protostar (like `starknet_py` or `cairo-lang`) should be available for importing by
default.
If you want to import other custom modules, you should extend `PYTHONPATH`
yourself (https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH), when running this command.
