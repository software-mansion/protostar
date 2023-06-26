use result::ResultTrait;
use protostar_print::PrintTrait;
use array::ArrayTrait;
use cheatcodes::PreparedContract;

#[test]
fn test_deploy_simple() {
    assert(1 == 1, 'simple check');
    let calldata = ArrayTrait::<felt252>::new();
    let class_hash = declare('deploy_test').expect('Could not declare');

    let contract_address = deploy(
        PreparedContract {
            class_hash,
            constructor_calldata:
            @calldata, contract_address: 'addr'
        }
    ).expect('Could not deploy');
    assert(contract_address == 'addr', 'incorrect contract_address');
}
