# `reflect`
```python
def reflect(self, ids: VmConsts) -> Reflector:
Reflector.get() -> Union[CairoStruct, RelocatableValue, int]
def CairoStruct(typename: str) -> Type # inherits from base CairoStruct
```
Lazily converts Cairo object into Python custom named `CairoStruct` (complex structure) or keeps it a simple type `RelocatableValue` (pointer) or `int` (felt). It can be used to easily print and compare complex structures.
```cairo title="./test/example_test.cairo"
%lang starknet

from starkware.cairo.common.registers import get_fp_and_pc

struct StructB:
    member e: felt
    member f: felt
end

struct StructA:
    member a: StructB
    member b: felt
    member c: StructB*
    member d: felt**
end

@external
func test_reflect_passed_full():
    alloc_locals

    let (__fp__, _) = get_fp_and_pc()

    local pointee: felt = 13
    local ptr: felt* = &pointee

    local structB: StructB = StructB(e=42, f=24)
    local structA: StructA = StructA(
        a = structB,
        b = 13,
        c = &structB,
        d = &ptr,
    )

    local ptrB: StructB* = &structB
    
    %{
        structA = reflect(ids).structA.get()
        ptrB = reflect(ids).ptrB.get()
        structB = reflect(ids).structB.get()
        f = reflect(ids).structB.f.get()

        print(structA)

        StructB = CairoStruct("StructB")
        StructA = CairoStruct("StructA")
        assert structA == StructA(
            a=StructB(
                e=42,
                f=24,
            ),
            b=13,
            c=ptrB,
            d=structA.d,
        )
    %}
    return ()
```
