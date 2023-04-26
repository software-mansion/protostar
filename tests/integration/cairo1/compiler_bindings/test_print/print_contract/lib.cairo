#[contract]
mod PrintContract {
    use protostar_print::PrintTrait;

    #[external]
    fn perform_print(a: felt252, b: felt252, c: felt252) {
        123.print();
        a.print();
        b.print();
        c.print();
    }
}