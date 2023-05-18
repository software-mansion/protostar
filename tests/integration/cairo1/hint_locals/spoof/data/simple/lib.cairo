#[contract]
mod SimpleContract {
    use box::BoxTrait;
    use starknet::info::get_tx_info;

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
}