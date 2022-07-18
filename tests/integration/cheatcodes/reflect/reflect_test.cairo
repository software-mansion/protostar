%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.registers import get_fp_and_pc

struct Struct1:
    member e: felt
    member f: felt
end

struct VoterInfo:
    member a: Struct1
    member b: felt
    member c: Struct1*
    member d: felt**
    member x: Struct1**
end

@external
func test_reflect_passed_assert():
    alloc_locals
    local value: VoterInfo
    local strct: Struct1
    local strct2: Struct1
    local ptr1: Struct1*
    local ptr: felt*
    local pointee: felt

    let (__fp__, _) = get_fp_and_pc()
    
    assert pointee = 13
    assert ptr = &pointee
    assert ptr1 = &strct2
    assert strct2.e = 14
    assert strct2.f = 15
    assert strct.e = 7
    assert strct.f = 8
    assert value.a = strct
    assert value.b = 2
    assert value.c = ptr1
    assert value.d = &ptr
    assert value.x = &ptr1

    %{
        value = reflect(ids.value)

        from collections import namedtuple
        Struct1 = namedtuple("Struct1", "e f")
        other = Struct1(e=7, f=8)
        assert value.a == other
       
    %}
    return ()
end

@external
func test_reflect_failed_assert():
    alloc_locals
    local value: VoterInfo
    local strct: Struct1
    local strct2: Struct1
    local ptr1: Struct1*
    local ptr: felt*
    local pointee: felt

    let (__fp__, _) = get_fp_and_pc()
    
    assert pointee = 13
    assert ptr = &pointee
    assert ptr1 = &strct2
    assert strct2.e = 14
    assert strct2.f = 15
    assert strct.e = 7
    assert strct.f = 8
    assert value.a = strct
    assert value.b = 2
    assert value.c = ptr1
    assert value.d = &ptr
    assert value.x = &ptr1

    %{
        value = reflect(ids.value)
        print(value)
        assert value.a.f == 42
    %}
    return ()
end

@external
func test_reflect_passed_assert_pointer():
    alloc_locals
    local value: VoterInfo
    local strct: Struct1
    local strct2: Struct1
    local ptr1: Struct1*
    local ptr: felt*
    local ptr3: felt**
    local pointee: felt

    let (__fp__, _) = get_fp_and_pc()
    
    assert pointee = 13
    assert ptr = &pointee
    assert ptr1 = &strct2
    assert strct2.e = 14
    assert strct2.f = 15
    assert strct.e = 7
    assert strct.f = 8
    assert value.a = strct
    assert value.b = 2
    assert value.c = ptr1
    assert value.d = &ptr
    assert value.x = &ptr1
    assert ptr3 = &ptr

    %{
        print(reflect(ids.ptr3))
        assert reflect(ids.value).d == reflect(ids.ptr3)
    %}
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
    
    %{ print(reflect(ids.node)) %}

    return()
end

@external
func test_reflect_failed_corruption():
    alloc_locals
    local strct: Struct1
    assert strct.e = 42
    assert strct.f = 24

    %{
        strct = reflect(ids.strct)
        strct.f = 69
    %}

    return ()
end


