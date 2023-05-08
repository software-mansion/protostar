#[abi]
trait IAnotherContract {
    fn foo();
}


#[contract]
mod TestContract {
    struct Storage { my_storage_var: felt252, }

    fn internal_func() -> felt252 {
        1
    }

    #[external]
    fn test(ref arg: felt252, arg1: felt252, arg2: felt252) -> felt252 {
        let x = my_storage_var::read();
        my_storage_var::write(x + 1);
        x + internal_func()
    }

    #[external]
    fn empty() {
    }
}