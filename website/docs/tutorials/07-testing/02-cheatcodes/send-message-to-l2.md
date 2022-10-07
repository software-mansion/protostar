# `send_message_to_l2`

```python
def send_message_to_l2(
        fn_name: str,
        from_address: int = 0,
        to_address: Optional[int] = None,
        payload: Optional[CairoOrPythonData] = None,
    ) -> None:
        ...
```

This cheatcode simulates an incoming message from l1 to l2 executed with `fn_name` at `to_address` contract address.
Can be useful when implementing i.e. a token bridge and wanting to test the message consuming behavior.
This cheatcode requires that the contract at `to_address` address has a `@l1_handler` named `fn_name`.

- `fn_name` — `@l1_handler` function name. 
- `from_address` — An l1 address with which the message will be sent.
- `to_address` — A l2 contract's address - the receiver of the message, which implements the called `@l1_handler`. Defaults to the current contract.
- `payload` — `@l1_handler` function parameters, without `from_address`. This can be passed as a dictionary, or as flat array of ints. Defaults to empty array. 

:::tip
You can leverage [data transformer](README.md#data-transformer) to pass payload as a dictionary instead of list of numbers.
:::

:::warning
Do not provide `from_address` (needed for all l1 handlers in StarkNet) in the function's `payload` - this is passed automatically using `from_address` parameter. 
:::