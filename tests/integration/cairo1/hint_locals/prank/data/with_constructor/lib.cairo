#[contract]
mod WithConstructor {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::ContractAddressIntoFelt252;
    use traits::Into;


    struct Storage {
        owner: ContractAddress,
    }

    #[constructor]
    fn constructor() {
        let caller_address = get_caller_address();
        owner::write(caller_address);
    }

    #[view]
    fn get_owner() -> felt252 {
        owner::read().into()
    }
}
