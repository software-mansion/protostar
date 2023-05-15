#[contract]
mod StoringTimestampContract {
    use starknet::info::get_block_info;
    use box::BoxTrait;

    struct Storage {
        stored_block_number: u64
    }

    #[external]
    fn store_block_number() {
        stored_block_number::write(get_block_info().unbox().block_number);
    }

    #[view]
    fn retrieve_stored() -> u64 {
        stored_block_number::read()
    }
}
