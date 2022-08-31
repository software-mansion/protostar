# `expect_revert`

```python
def expect_revert(error_type: Optional[str] = None, error_message: Optional[str] = None) -> None: ...
```

If a code beneath `expect_revert` raises a specified exception, a test will pass. If not, a test will fail.

:::warning
`expect_revert` doesn't work as try/catch. Protostar stops executing test case after catching a revert error.
:::

:::info
Protostar displays an error type and a message when a test fails.
:::

```cairo title="This test passes despite calling an uninitialized contract."
%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_failing_to_call_external_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=21, amount=3)

    return ()
end
```


```cairo title="'except_revert' checks if the last error annotation contains 'error_message'."
%lang starknet

func inverse(x) -> (res):
    with_attr error_message("x must not be zero. Got x={x}."):
        return (res=1 / x)
    end
end

func assert_not_equal(a, b):
    let diff = a - b
    with_attr error_message("a and b must be distinct."):
        inverse(diff)
    end
    return ()
end

@external
func test_error_message{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert(error_message="must be distinct") %}
    assert_not_equal(0, 0)
    return ()
end
```

:::tip
Use [scope attributes](https://www.cairo-lang.org/docs/how_cairo_works/scope_attributes.html?highlight=with_attr) to annotate a code block with an informative error message.
:::
