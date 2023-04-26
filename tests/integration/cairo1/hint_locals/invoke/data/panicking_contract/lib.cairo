use array::ArrayTrait;

#[contract]
mod PanickingContract {
    use array::ArrayTrait;

    #[external]
    fn go_bonkers() {
        let mut panic_data = ArrayTrait::new();
        panic_data.append('i am bonkers');
        panic(panic_data);
    }
}
