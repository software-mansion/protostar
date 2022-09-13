%lang starknet

from starkware.starknet.common.syscalls import get_contract_address
from starkware.starknet.common.syscalls import deploy
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace ProxyContract {
    func set_target(new_target: felt) {
    }

    func increase_twice(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@contract_interface
namespace BasicContract {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@contract_interface
namespace BasicWithConstructor {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@contract_interface
namespace BasicWithConstructorNoArgs {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@external
func __setup__() {
    %{ context.basic_contract = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_contract.cairo") %}

    return ();
}

@external
func test_deploy_contract{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    local contract_address: felt;
    %{
        declared = declare("./tests/integration/cheatcodes/deploy_contract/basic_contract.cairo")
        prepared = prepare(declared)
        contract = deploy(prepared)
        ids.contract_address = contract.contract_address
    %}

    BasicContract.increase_balance(contract_address, 5);
    let (res) = BasicContract.get_balance(contract_address);
    assert res = 5;
    return ();
}

@external
func test_deploy_contract_simplified{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    local contract_address: felt;
    %{ ids.contract_address = context.basic_contract.contract_address %}

    BasicContract.increase_balance(contract_address, 5);
    let (res) = BasicContract.get_balance(contract_address);
    assert res = 5;
    return ();
}

@external
func test_deploy_contract_with_constructor{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local contract_address: felt;
    %{ ids.contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo", [41]).contract_address %}
    BasicWithConstructor.increase_balance(contract_address, 1);
    let (res) = BasicWithConstructor.get_balance(contract_address);
    assert res = 42;
    return ();
}

@external
func test_deploy_contract_with_constructor_steps{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local contract_address: felt;
    %{
        declared = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo")
        prepared = prepare(declared, [41])
        ids.contract_address = deploy(prepared).contract_address
    %}
    BasicWithConstructor.increase_balance(contract_address, 1);
    let (res) = BasicWithConstructor.get_balance(contract_address);
    assert res = 42;
    return ();
}

@external
func test_deploy_contract_pranked{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    %{
        declared_1 = declare("./tests/integration/cheatcodes/deploy_contract/pranked_contract.cairo")
        declared_2 = declare("./tests/integration/cheatcodes/deploy_contract/pranked_contract.cairo")

        prepared_1 = prepare(declared_1, [111])
        prepared_2 = prepare(declared_2, [222])

        start_prank(111, target_contract_address=prepared_1.contract_address)
        start_prank(222, target_contract_address=prepared_2.contract_address)

        deploy(prepared_1)
        deploy(prepared_2)
    %}
    return ();
}

@external
func test_deploy_the_same_contract_twice{syscall_ptr: felt*, range_check_ptr}() {
    %{
        declared_1 = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo")
        declared_2 = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo")

        prepared_1 = prepare(declared_1, [42])
        prepared_2 = prepare(declared_2, [42])

        deploy(prepared_1)
        deploy(prepared_2)
    %}
    return ();
}

@external
func test_deploy_using_syscall{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local class_hash: felt;
    %{ ids.class_hash = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo").class_hash %}
    let (local calldata: felt*) = alloc();
    assert calldata[0] = 41;
    let (contract_address) = deploy(class_hash, 34124, 1, calldata, 0);

    BasicWithConstructor.increase_balance(contract_address, 1);
    let (res) = BasicWithConstructor.get_balance(contract_address);
    assert res = 42;
    return ();
}

@external
func test_deploy_using_syscall_non_zero_flag{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local class_hash: felt;
    %{ ids.class_hash = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo").class_hash %}
    let (local calldata: felt*) = alloc();
    assert calldata[0] = 41;
    let (contract_address) = deploy(class_hash, 34124, 1, calldata, 1);

    BasicWithConstructor.increase_balance(contract_address, 1);
    let (res) = BasicWithConstructor.get_balance(contract_address);
    assert res = 42;
    return ();
}

@external
func test_syscall_after_deploy{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local contract_address: felt;
    %{ ids.contract_address = context.basic_contract.contract_address %}

    BasicWithConstructor.increase_balance(contract_address, 1);
    let (res) = get_contract_address();
    return ();
}

@external
func test_utilizes_cairo_path{syscall_ptr: felt*, range_check_ptr}() {
    %{
        declared = declare("./tests/integration/cheatcodes/deploy_contract/contract_using_external.cairo")
        prepared = prepare(declared)
        deploy(prepared).contract_address
    %}
    return ();
}

@contract_interface
namespace BasicWithConstructorUint256 {
    func increase_balance(amount: Uint256) {
    }

    func get_balance() -> (res: Uint256) {
    }
}

@external
func test_passing_constructor_data_as_list{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local deployed_contract_address: felt;

    %{
        ids.deployed_contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo",
            [42, 0]
        ).contract_address
    %}

    let (balance) = BasicWithConstructorUint256.get_balance(deployed_contract_address);

    assert balance.low = 42;
    assert balance.high = 0;

    return ();
}

@external
func test_data_transformation{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local deployed_contract_address: felt;

    %{
        ids.deployed_contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo",
            { "initial_balance": 42 }
        ).contract_address
    %}

    let (balance) = BasicWithConstructorUint256.get_balance(deployed_contract_address);

    assert balance.low = 42;
    assert balance.high = 0;

    return ();
}

@external
func test_constructor_no_args_executed{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local deployed_contract_address: felt;

    %{
        ids.deployed_contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_no_args.cairo").contract_address
    %}

    let (balance) = BasicWithConstructorNoArgs.get_balance(deployed_contract_address);

    assert balance = 42;

    return ();
}

@contract_interface
namespace EventEmitterContainer {
    func emit() {
    }
}

@event
func fake_event() {
}


@external
func test_emitting_events_from_user_contract_constructor_and_from_current_contract{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    %{
        deploy_contract("./tests/integration/cheatcodes/deploy_contract/event_emitter_contract.cairo").contract_address
    %}
    fake_event.emit();
    return ();
}