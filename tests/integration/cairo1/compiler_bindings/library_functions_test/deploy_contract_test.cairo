use array::ArrayTrait;
use result::ResultTrait;


#[test]
fn test_deploy_contract() {
   let mut arr = ArrayTrait::new();
   let deployed = deploy_contract('test', arr).unwrap();
   assert(deployed == 132, 'deployed == 132')
}
