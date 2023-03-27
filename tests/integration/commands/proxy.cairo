%lang starknet

from starkware.starknet.common.syscalls import library_call, library_call_l1_handler
from starkware.starknet.common.syscalls import get_caller_address

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.cairo.common.math import assert_not_zero


@event
func Upgraded(implementation: felt) {
}

@event
func AdminChanged(previousAdmin: felt, newAdmin: felt) {
}


@storage_var
func Proxy_implementation_hash() -> (implementation: felt) {
}

@storage_var
func Proxy_admin() -> (admin: felt) {
}

@storage_var
func Proxy_initialized() -> (initialized: felt) {
}

func initializer{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    proxy_admin: felt
) {
    let (initialized) = Proxy_initialized.read();
    with_attr error_message("Proxy: contract already initialized") {
        assert initialized = FALSE;
    }

    Proxy_initialized.write(TRUE);
    _set_admin(proxy_admin);
    return ();
}

func get_implementation_hash{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    ) -> (implementation: felt) {
    return Proxy_implementation_hash.read();
}

func get_admin{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    admin: felt
) {
    return Proxy_admin.read();
}

func _set_admin{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    new_admin: felt
) {
    let (previous_admin) = get_admin();
    Proxy_admin.write(new_admin);
    AdminChanged.emit(previous_admin, new_admin);
    return ();
}

func _set_implementation_hash{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    new_implementation: felt
) {
    with_attr error_message("Proxy: implementation hash cannot be zero") {
        assert_not_zero(new_implementation);
    }

    Proxy_implementation_hash.write(new_implementation);
    Upgraded.emit(new_implementation);
    return ();
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    implementation_hash: felt, selector: felt,
    calldata_len: felt, calldata: felt*
) {
    alloc_locals;
    _set_implementation_hash(implementation_hash);

    if (selector != 0) {
        // Initialize proxy from implementation
        library_call(
            class_hash=implementation_hash,
            function_selector=selector,
            calldata_size=calldata_len,
            calldata=calldata,
        );
    }

    return ();
}

@external
@raw_input
@raw_output
func __default__{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    selector: felt, calldata_size: felt, calldata: felt*
) -> (retdata_size: felt, retdata: felt*) {
    let (class_hash) = get_implementation_hash();

    let (retdata_size: felt, retdata: felt*) = library_call(
        class_hash=class_hash,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    );
    return (retdata_size, retdata);
}

@l1_handler
@raw_input
func __l1_default__{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    selector: felt, calldata_size: felt, calldata: felt*
) {
    let (class_hash) = get_implementation_hash();
    library_call_l1_handler(
        class_hash=class_hash,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    );
    return ();
}