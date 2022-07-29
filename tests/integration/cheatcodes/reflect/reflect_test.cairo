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
func test_reflect_passed_simple():
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

    %{
        structA = reflect.structA.get()

        StructB = CairoStruct
        other = StructB(e=42, f=24)

        assert structA.a == other
    %}
    return ()
end

@external
func test_reflect_failed_simple():
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

    %{
        structA = reflect.structA.get()
        assert structA.a.f == 42
    %}
    return ()
end

@external
func test_reflect_passed_pointer():
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

    %{ assert reflect.structA.c.get() == reflect.ptrB.get() %}
    return ()
end

struct Node:
    member next: Node*
end

@external
func test_reflect_passed_pointer_loop():
    alloc_locals

    local node: Node
    let (__fp__, _) = get_fp_and_pc()
    
    assert node.next = &node
    
    %{ print(reflect.node.get()) %}

    return()
end

@external
func test_reflect_failed_corruption():
    alloc_locals
    local structB: StructB = StructB(e=42, f=24)

    %{
        structB = reflect.structB.get()
        structB.f = 69
    %}

    return ()
end


@external
func test_reflect_passed_repr():
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

    %{
        value = reflect.structA.get()

        print(str(value))

        assert str(value).strip() == """
        CairoStruct(
            a=CairoStruct(
                e=42
                f=24
            )
            b=13
            c=1:10
            d=1:9
        )""".strip()
    %}
    return ()
end

@external
func test_reflect_passed_type_pointer():
    alloc_locals

    let (__fp__, _) = get_fp_and_pc()

    local a: felt = 123454321
    local structB: StructB = StructB(e=42, f=24)
    local ptrB: StructB* = &structB
    local ptrA: felt* = &a
    
    %{
        # ids.T* -> T, reflect.T* -> T*
        # pointers (RelocatableValue) are not type safe
        assert type(reflect.ptrB.get()) == type(reflect.ptrA.get())
    %}
    return ()
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
        structA = reflect.structA.get()
        ptrB = reflect.ptrB.get()
        structB = reflect.structB.get()
        f = reflect.structB.f.get()

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
end

@external
func test_reflect_failed_illegal_arg():    
    %{
        structC = reflect.structC.get()
        print(structC)
    %}
    return ()
end

@external
func test_reflect_failed_getattr_felt(): 
    alloc_locals

    let f: felt = 1010101

    %{
        invalid = reflect.f.invalid.get()
    %}
    return ()
end

@external
func test_reflect_failed_getattr_pointer():    
    alloc_locals

    let (__fp__, _) = get_fp_and_pc()

    local structB: StructB = StructB(e=42, f=24)
    local ptrB: StructB* = &structB

    %{
        invalid = reflect.ptrB.f.get()
    %}
    return ()
end

@external
func test_reflect_failed_invalid_member():    
    alloc_locals
    local structB: StructB = StructB(e=42, f=24)

    %{
        invalid = reflect.structB.g.get()
    %}
    return ()
end

@external
func test_reflect_failed_get_on_none():
    %{
        invalid = reflect.get()
    %}
    return ()
end
