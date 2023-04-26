use array::ArrayTrait;

#[contract]
mod PanickingContract {
    use array::ArrayTrait;

    #[external]
    fn go_bonkers() {
        assert(false, 'i am bonkers');
    }
}
