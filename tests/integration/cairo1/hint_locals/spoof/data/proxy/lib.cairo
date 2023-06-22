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
    fn check_remote_nonce(at: ContractAddress) -> felt252 {
        let res = call_contract_syscall(
            at,
            // selector of 'get_nonce'
            756703644403488948674317127005533987569832834207225504298785384568821383277,
            ArrayTrait::new().span()
        ).unwrap_syscall();

        *res.at(0_usize)
    }

    #[view]
    fn get_nonce() -> felt252 {
        get_tx_info().unbox().nonce
    }
}
