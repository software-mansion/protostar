use array::ArrayTrait;

#[test]
#[available_gas(1000001)]
fn passing_test(){
    match gas::get_gas() {
        Option::Some(_) => {},
        Option::None(_) => {
            let mut data = ArrayTrait::new();
            data.append('Out of gas');
            panic(data);
        },
    }
    assert(1 == 1, 'simple check');
}

