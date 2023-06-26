#[contract]
mod SimpleContract {
    use box::BoxTrait;
    use starknet::info::get_tx_info;
    use starknet::contract_address::ContractAddress;

    struct Storage {
        stored_hash: felt252
    }

    #[external]
    fn store_tx_hash() {
        let tx_info = get_tx_info().unbox();
        stored_hash::write(tx_info.transaction_hash);
    }

    #[view]
    fn get_stored_tx_hash() -> felt252 {
        stored_hash::read()
    }

    #[view]
    fn get_transaction_version() -> felt252 {
        let tx_info = get_tx_info().unbox();
        tx_info.version
    }

    #[view]
    fn get_account_contract_address() -> ContractAddress {
        let tx_info = get_tx_info().unbox();
        tx_info.account_contract_address
    }

    #[view]
    fn get_max_fee() -> u128 {
        let tx_info = get_tx_info().unbox();
        tx_info.max_fee
    }

    #[view]
    fn get_signature() -> Span::<felt252> {
        let tx_info = get_tx_info().unbox();
        tx_info.signature
    }

    #[view]
    fn get_chain_id() -> felt252 {
        let tx_info = get_tx_info().unbox();
        tx_info.chain_id
    }

    #[view]
    fn get_nonce() -> felt252 {
        let tx_info = get_tx_info().unbox();
        tx_info.nonce
    }
}