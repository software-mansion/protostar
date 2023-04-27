#[contract]
mod PrankedContract {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::ContractAddressIntoFelt252;
    use option::Option;
    use traits::Into;

    struct Storage {
        a: felt252
    }

    #[external]
    fn maybe_set_three() {
        let caller_address: ContractAddress = get_caller_address();
        if (caller_address.into() == 123) {
            a::write(3);
        } else {
            a::write(2);
        }
    }

    #[view]
    fn get_a() -> felt252 {
        a::read()
    }
}
