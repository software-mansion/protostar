# `reflect`
```python
def reflect(self, ids) -> Reflector:
```
Loads specified Cairo object into Python type. Returns `Reflector` object that works simillarly to `ids`. To retrieve the value use `get()` method which can return:

- `int` (for felt)
- `RelocatableValue` (for pointer)
- `CairoStruct` (for more complex types)

You can use it to print cairo data and compare complex structures.

```cairo title=Printing
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


```cairo title=Pointers
%lang starknet

from starkware.cairo.common.registers import get_fp_and_pc

@external
func test_pointers():
    alloc_locals

    let (__fp__, _) = get_fp_and_pc()

    local pointee: felt = 13
    local ptr1: felt* = &pointee
    local ptr2: felt* = &pointee
    
    %{
        ptr1 = reflect(ids).ptr1.get()
        ptr2 = reflect(ids).ptr2.get()

        print(ptr1) # output: 1:8
        print(type(ptr1)) # output: RelocatableValue
        assert ptr1 == ptr2  # Pointers are compared directly using their addresses
    %}
    return ()
end
```

```cairo title=Nested comparisons
%lang starknet

struct InnerStruct:
    member value: felt
end

struct OuterStruct:
    member inner_struct: InnerStruct
end

@external
func test_nesting():
    alloc_locals
    local inner_struct: InnerStruct = InnerStruct(value=7)
    local outer_struct: OuterStruct = OuterStruct(inner_struct=inner_struct)

    %{
        outer_struct = reflect(ids).outer_struct.get()
        OuterStruct = CairoStruct #
        InnerStruct = CairoStruct # This way you can add aliases for readability

        # You can compare nested structs
        assert outer_struct == OuterStruct(
            inner_struct=InnerStruct(
                value=7
            )
        )
    %}
    return ()
end
```


```cairo title=Wildcards
%lang starknet

struct TwoFieldStruct:
    member value1: felt
    member value2: felt
end

@external
func test_wildcards():
    alloc_locals
    local two_field_struct: TwoFieldStruct = TwoFieldStruct(value1=23, value2=17)
    
    %{
        two_field_struct = reflect(ids).two_field_struct.get()
        assert two_field_struct == CairoStruct(
            value1=23,
            value2=two_field_struct.value2
            # You can use struct members in comparison to make sure it evaluates to true
        )
    %}
    return ()
end
```

:::warning
Unlike `ids`, `reflect` does not automatically dereference pointers. Currently you have to dereference them in Cairo.
:::

:::warning
`reflect` does not work for references created with `let`.
:::