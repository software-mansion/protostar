# `expect_events`
```python
 def expect_events(
            *raw_expected_events: Union[
                str, # Protostar interprets string as an event's name 
                TypedDict("ExpectedEvent", {
                    "name": str,
                    "data": NotRequired[Union[
                      List[int],
                      Dict[
                        # e.g.
                        # {"current_balance" : 37, "amount" : 21}
                        # 
                        # for the following event signature:
                        # @event
                        # func balance_increased(current_balance : felt, amount : felt):
                        # end
                        DataTransformer.ArgumentName,
                        DataTransformer.SupportedType,
                      ]
                    ]],
                    "from_address": NotRequired[int]
                },
            )],
        ) -> None: ...
```
Compares expected events with events in the StarkNet state. You can use this cheatcode to test whether a contract emits specified events. Protostar compares events after a test case is completed. Therefore, you can use this cheatcode in any place within a test case.

:::tip
You can provide `"data"` as a dictionary to leverage [data transformer](/docs/tutorials/guides/testing#data-transformer).
:::

```cairo title="Protostar also checks the order of emitted events."
%lang starknet

@event
func foobar(number : felt):
end

func emit_foobar{syscall_ptr : felt*, range_check_ptr}(number : felt):
    foobar.emit(number)
    return ()
end

@contract_interface
namespace BasicContract:
    func increase_balance():
    end
end

# ----------------------------------------------

@external
func test_expect_events_are_in_declared_order{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@external
func test_expect_event_by_contract_address{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": ids.contract_address})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end
```
