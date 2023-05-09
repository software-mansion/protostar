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
    fn check_remote_timestamp(at: ContractAddress) -> felt252 {
        let res = call_contract_syscall(
            at,
            1629366970795695773070250980946704058198029661891218027632744717191545197319,
            ArrayTrait::new().span()
        ).unwrap_syscall();

        *res.at(0_usize)
    }
}
