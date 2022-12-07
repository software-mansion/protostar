# `expect_events`
```python
class ExpectedEventData(TypedDict):
    name: str
    data: NotRequired[list[int] | dict[str, Any] | None]
    from_address: NotRequired[int]

ExpectedEventName = str

ExpectedEvent = ExpectedEventData | ExpectedEventName

def expect_events(*expected_events: ExpectedEvent) -> None: ...
```
Compares expected events with events in the StarkNet state. You can use this cheatcode to test whether a contract emits specified events. Protostar compares events after a test case is completed. Therefore, you can use this cheatcode in any place within a test case.

```cairo title="Protostar also checks the order of emitted events."
%lang starknet

@event
func foobar(number: felt) {
}

func emit_foobar{syscall_ptr: felt*, range_check_ptr}(number: felt) {
    foobar.emit(number);
    return ();
}

@contract_interface
namespace BasicContract {
    func increase_balance() {
    }
}

// ----------------------------------------------

@external
func test_expect_events_are_in_declared_order{syscall_ptr: felt*, range_check_ptr}() {
    %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
    emit_foobar(21);
    emit_foobar(37);
    return ();
}

@external
func test_expect_event_by_contract_address{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local contract_address: felt;
    %{
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": ids.contract_address})
    %}
    BasicContract.increase_balance(contract_address=contract_address);
    return ();
}
```

:::tip
You can provide `"data"` as a dictionary to leverage [data transformer](README.md#data-transformer) - see example below
:::


```cairo title="Emitting a complex structured event, and expecting it in tests using data transformer"
%lang starknet

struct InnerStruct {
    b : felt,
    c : felt,
}

struct DeeplyNestedStruct {
    inner : InnerStruct,
    a : felt,
}

@event
func structured_event(structure: DeeplyNestedStruct, side_arg: felt) {
}

func emit_structured_event{syscall_ptr: felt*, range_check_ptr}(number: felt) {
    let inner_struct = InnerStruct(
        b=number + 1,
        c=number + 2,
    );

    let deeply_nested = DeeplyNestedStruct(
        inner=inner_struct,
        a=number,
    );

    structure_event.emit(deeply_nested);
    return ();
}

// ----------------------------------------------

@external
func test_emitting_struct_with_data_transformer{syscall_ptr: felt*, range_check_ptr}() {
    %{
        expect_events({
            "name": "structured_event",
            "data": {
                "structure": {
                    "a": 21,
                    "inner": {
                        "b": 22,
                        "c": 23,
                    }
                },
                "side_arg": 37
            }
        })
    %}
    emit_structured_event(21, 37);
    return ();
}
```