#[contract]
mod MinimalContract {
    use starknet::info::get_block_info;
    use box::BoxTrait;

    #[view]
    fn check_timestamp() -> u64 {
        get_block_info().unbox().block_timestamp
    }
}
