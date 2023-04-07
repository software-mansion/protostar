use external_contract::contract::SampleContract::InnerStruct;

#[test]
fn test_importing_from_contract(){
    let obj = InnerStruct { a: 12 };
    assert(obj.a == 12, 'obj.a == 12');
}