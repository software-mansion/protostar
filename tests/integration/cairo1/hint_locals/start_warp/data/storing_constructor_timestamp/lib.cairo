#[contract]
mod StoringConstructorTimestampContract {
    use starknet::info::get_block_info;
    use box::BoxTrait;

    struct Storage {
        stored_timestamp: u64
    }

    fn store_timestamp() {
        stored_timestamp::write(get_block_info().unbox().block_timestamp);
    }

    #[constructor]
    fn constructor() {
        store_timestamp()
    }

    #[view]
    fn retrieve_stored() -> u64 {
        stored_timestamp::read()
    }
}
