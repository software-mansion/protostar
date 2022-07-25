# `reflect`
```python
def reflect(self, ids: VmConsts) -> Reflector:

class Reflector:
    def get(self)
```
Loads specified Cairo object into Python type. ```get()``` can return:

- int (for felt)
- RelocatableValue (for pointer)
- Cairo Struct (for more complex types)

You can use it to print cairo data and compare complex structures.

```cairo title="./test/simple_example_test.cairo"
%lang starknet

struct SimpleStruct:
    member x: felt
end

@external
func test_reflect_simple():
    alloc_locals

    local simple_struct: SimpleStruct = SimpleStruct(x=10)

    %{
        simple_struct = reflect(ids).simple_struct.get()
        print(simple_struct)
        # output:
        # CairoStruct(
        #     x=10
        # )

        assert simple_struct.x == 10 # true
    %}

    return()
end
```

```cairo title="./test/complex_example_test.cairo"
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

        StructB = CairoStruct
        StructA = CairoStruct
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

:::warning
Unlike `ids`, `reflect` does not automatically dereference pointers. As of right now you have to dereference them in Cairo.
:::
