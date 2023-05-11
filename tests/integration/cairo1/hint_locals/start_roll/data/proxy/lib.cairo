use starknet::syscalls::call_contract_syscall;
use array::ArrayTrait;
use starknet::SyscallResult;
use starknet::contract_address::ContractAddress;
use array::SpanTrait;

#[contract]
mod ProxyContract {
    use starknet::syscalls::call_contract_syscall;
    use array::ArrayTrait;
    use starknet::SyscallResult;
    use starknet::contract_address::ContractAddress;
    use array::SpanTrait;

    #[view]
    fn check_remote_block_number(at: ContractAddress) -> felt252 {
        let res = call_contract_syscall(
            at,
            // selector of 'check_block_number'
            459172859953536820914018703131660971355179475026043993953743754883304096163,
            ArrayTrait::new().span()
        ).unwrap_syscall();

        *res.at(0_usize)
    }
}
