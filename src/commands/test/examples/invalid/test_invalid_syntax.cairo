%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@invalid_syntax
func test_broken{syscall_ptr : felt*, range_check_ptr}():
end
