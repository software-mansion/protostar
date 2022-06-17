%lang starknet

@view
func test_wrong_constructor_args_of_deploy_contract{}():
    %{ deploy_contract("./tests/integration/constructor_in_tested_file/basic_contract.cairo") %}

    return ()
end
