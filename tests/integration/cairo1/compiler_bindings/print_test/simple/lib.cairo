#[contract]
mod SimpleContract {
    use protostar_print::PrintTrait;

    #[external]
    fn perform(a: felt252, b: felt252, c: felt252) {
        123.print();
        a.print();
        b.print();
        c.print();
    }
}