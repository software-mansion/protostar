use crate::helpers::constants::{ACCOUNT, ACCOUNT_FILE_PATH, CONTRACTS_DIR, NETWORK, URL};
use camino::Utf8PathBuf;
use cast::{get_account, get_network, get_provider};
use starknet::accounts::{Account, SingleOwnerAccount};
use starknet::contract::ContractFactory;
use starknet::core::types::contract::{CompiledClass, SierraClass};
use starknet::core::types::FieldElement;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::JsonRpcClient;
use starknet::signers::LocalWallet;
use std::sync::Arc;

pub fn sierra_balance_path() -> String {
    CONTRACTS_DIR.to_string() + "/balance/target/dev/balance_SimpleBalance.sierra.json"
}

pub fn casm_balance_path() -> String {
    CONTRACTS_DIR.to_string() + "/balance/target/dev/balance_SimpleBalance.casm.json"
}

pub async fn declare_deploy_simple_balance_contract() {
    let provider = get_provider(URL).expect("Could not get the provider");
    let account = get_account(
        ACCOUNT,
        &Utf8PathBuf::from(ACCOUNT_FILE_PATH),
        &provider,
        &get_network(NETWORK).expect("Could not get the network"),
    )
    .expect("Could not get the account");

    let contract_definition: SierraClass = {
        let file_contents =
            std::fs::read(sierra_balance_path()).expect("Could not read balance's sierra file");
        serde_json::from_slice(&file_contents).expect("Could not cast sierra file to SierraClass")
    };
    let casm_contract_definition: CompiledClass = {
        let file_contents =
            std::fs::read(casm_balance_path()).expect("Could not read balance's casm file");
        serde_json::from_slice(&file_contents).expect("Could not cast casm file to CompiledClass")
    };

    let casm_class_hash = casm_contract_definition
        .class_hash()
        .expect("Could not compute class_hash");

    let declaration = account.declare(
        Arc::new(
            contract_definition
                .flatten()
                .expect("Could not flatten SierraClass"),
        ),
        casm_class_hash,
    );
    let declared = declaration.send().await.unwrap();

    let factory = ContractFactory::new(declared.class_hash, account, );
    let deployment = factory.deploy(Vec::new(), FieldElement::ONE, false, );
    deployment.send().await.unwrap();
}

pub fn default_cli_args() -> Vec<&'static str> {
    vec![
        "--url",
        URL,
        "--network",
        NETWORK,
        "--accounts-file",
        ACCOUNT_FILE_PATH,
        "--account",
        ACCOUNT,
    ]
}
