# Signing
Protostar offers two ways of providing the signature:

### 1. StarkCurveSigner

By default, Protostar uses the [StarkCurveSigner class](https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.stark_curve_signer.StarkCurveSigner) from Starknet.py.

This way requires you to pass a private key (for signing) and account contract's address (to fetch the nonce).
You can obtain the key and account address e.g. from [Argentx](https://chrome.google.com/webstore/detail/argent-x/dlcobpjiigpikoobohmabehhmhfoodbb) or [Braavos](https://chrome.google.com/webstore/detail/braavos-wallet/jnlgamecbpmbajjfhmmmlhejkemejdma) wallets. 

2 options are used for this:
- `private-key-path` - a path to the file containing hex-encoded private key
- `account-address` - your account contract's address (hex-encoded as well) on the appropriate network

Alternatively, if you prefer not to store private key in a file, we check for `PROTOSTAR_ACCOUNT_PRIVATE_KEY` environment variable, and use it if it's available.   
It should be in the same hex-encoded format, like all the options above.

### 2. Using a custom signer class

You can provide a custom signer class which inherits from [BaseSigner](https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner) abstract class. 
This way of signing requires you to write a class in Python, which signs the transaction in a way that is suitable to you.
After writing such class, simply use `signer_class` argument in the CLI for `declare` command to use that class instead of the default one.
Usage of this way of signing is exclusive with the default signer strategy.

:::caution
The custom signer class must not take any arguments in the constructor, since we don't pass any args on instantiation.
:::

The Python file containing this class can be put next to Cairo source code.
Protostar synchronizes `PYTHONPATH` with project's `cairo_path`.
Modules that are dependencies of Protostar (like `starknet_py` or `cairo-lang`) should be available for importing by default.
If you want to import other custom modules, you should extend `PYTHONPATH` yourself (https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH), when running this command.
