
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_declare() {
    match declare('minimal.cairo) { // missing ' here
        Result::Ok(_) => (),
        Result::Err(x) => {
            let mut data = ArrayTrait::new();
            data.append(x);
            panic(data)
        },
    }
}
