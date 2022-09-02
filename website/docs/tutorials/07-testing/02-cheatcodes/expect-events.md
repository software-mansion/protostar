# `expect_events`
```python
class EventExpectationDict(TypedDict):
    name: str
    data: NotRequired[list[int] | dict[str, Any]]
    from_address: NotRequired[int]

EventExpectationName = str

EventExpectation = EventExpectationDict | EventExpectationName

def expect_events(*expectations: EventExpectation) -> None: ...
```
Compares expected events with events in the StarkNet state. You can use this cheatcode to test whether a contract emits specified events. Protostar compares events after a test case is completed. Therefore, you can use this cheatcode in any place within a test case.

:::tip
You can provide `"data"` as a dictionary to leverage [data transformer](README.md#data-transformer).
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
